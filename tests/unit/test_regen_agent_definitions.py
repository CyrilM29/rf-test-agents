"""Tests du générateur de chat modes VS Code depuis `.claude/agents/rf-*.md`
(`scripts/regen_agent_definitions.py`) : traduction du frontmatter, mode
``--check``, et alignement réel des chat modes committés."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "scripts"))

import regen_agent_definitions as regen  # noqa: E402


AGENT = """---
name: rf-demo
version: 1.2.3
description: Agent de démonstration.
tools: Read, Glob, Write, Bash, mcp__rf-mcp__execute_step
---

Corps de l'agent : instructions.
"""


def make_repo(tmp_path: Path, agent_text: str = AGENT,
              name: str = "rf-demo.md") -> Path:
    (tmp_path / ".claude" / "agents").mkdir(parents=True)
    (tmp_path / ".claude" / "agents" / name).write_text(
        agent_text, encoding="utf-8")
    return tmp_path


class TestTraductionDesOutils:
    def test_builtins_traduits_et_ordonnes(self):
        assert regen.map_tools("Write, Read, Glob") == [
            "edit/createFile", "edit/createDirectory",
            "search/fileSearch", "search/readFile"]

    def test_outil_mcp_qualifie_par_son_serveur(self):
        assert regen.map_tools("mcp__rf-mcp__get_session_state") == [
            "rf-mcp/get_session_state"]

    def test_builtins_dedupliques(self):
        # Bash et PowerShell mappent tous deux vers runCommands.
        assert regen.map_tools("Bash, PowerShell") == ["runCommands"]

    def test_outil_inconnu_echoue_bruyamment(self):
        with pytest.raises(ValueError, match="no VS Code mapping"):
            regen.map_tools("OutilInexistant")

    def test_nom_mcp_malforme_echoue(self):
        with pytest.raises(ValueError, match="unrecognized MCP tool"):
            regen.map_tools("mcp__incomplet")


class TestFrontMatter:
    def test_parse_frontmatter_plat(self):
        meta, body = regen.parse_front_matter(AGENT)
        assert meta["name"] == "rf-demo"
        assert body.startswith("\nCorps de l'agent")

    def test_absence_de_frontmatter_echoue(self):
        with pytest.raises(ValueError, match="missing front matter"):
            regen.parse_front_matter("# Pas de frontmatter\n")

    def test_frontmatter_non_termine_echoue(self):
        with pytest.raises(ValueError, match="unterminated front matter"):
            regen.parse_front_matter("---\nname: x\n")


class TestGeneration:
    def test_chatmode_rendu(self, tmp_path):
        repo = make_repo(tmp_path)
        (dest, content), = regen.iter_renders(repo)
        assert dest.name == "rf-demo.chatmode.md"
        assert content.startswith("---\ndescription: ")
        assert "FICHIER GÉNÉRÉ" in content        # bannière anti-édition
        assert ".claude/agents/rf-demo.md" in content
        assert "Corps de l'agent" in content      # corps copié tel quel
        assert "name:" not in content.split("---")[1]  # clé Claude Code retirée

    def test_ecriture_puis_check_ok(self, tmp_path):
        repo = make_repo(tmp_path)
        assert regen.main(["--root", str(repo)]) == 0
        assert regen.main(["--root", str(repo), "--check"]) == 0

    def test_check_detecte_un_chatmode_manquant(self, tmp_path):
        repo = make_repo(tmp_path)
        assert regen.main(["--root", str(repo), "--check"]) == 1

    def test_check_detecte_une_edition_a_la_main(self, tmp_path):
        repo = make_repo(tmp_path)
        regen.main(["--root", str(repo)])
        cible = repo / ".github" / "chatmodes" / "rf-demo.chatmode.md"
        cible.write_text(cible.read_text(encoding="utf-8") + "\nédité\n",
                         encoding="utf-8")
        assert regen.main(["--root", str(repo), "--check"]) == 1

    def test_aucune_definition_echoue(self, tmp_path):
        (tmp_path / ".claude" / "agents").mkdir(parents=True)
        with pytest.raises(FileNotFoundError):
            regen.iter_renders(tmp_path)


class TestVersion:
    """Règle du 2026-09-29 : chaque définition porte la version de release du
    dépôt, la même pour tous ses agents, et les cibles la portent aussi."""

    def test_la_banniere_porte_la_version(self, tmp_path):
        (_, content), = regen.iter_renders(make_repo(tmp_path))
        assert "rf-demo.md, version 1.2.3 ;" in content
        assert "version" not in content.split("---")[1]  # pas dans le frontmatter VS Code

    def test_version_absente_refusee(self, tmp_path):
        repo = make_repo(tmp_path, AGENT.replace("version: 1.2.3\n", ""))
        with pytest.raises(ValueError, match="lacks 'version'"):
            regen.iter_renders(repo)

    @pytest.mark.parametrize("valeur", ["1.2", "v1.2.3", "1.2.3-rc1", "latest"])
    def test_version_mal_formee_refusee(self, tmp_path, valeur):
        repo = make_repo(tmp_path, AGENT.replace("1.2.3", valeur))
        with pytest.raises(ValueError, match="is not X.Y.Z"):
            regen.iter_renders(repo)

    def test_deux_agents_en_desaccord_refuses_en_les_nommant(self, tmp_path):
        repo = make_repo(tmp_path)
        (repo / ".claude" / "agents" / "rf-autre.md").write_text(
            AGENT.replace("rf-demo", "rf-autre").replace("1.2.3", "1.2.4"),
            encoding="utf-8")
        with pytest.raises(ValueError, match="rf-autre.md=1.2.4, rf-demo.md=1.2.3"):
            regen.iter_renders(repo)

    def test_un_changement_de_version_rend_les_cibles_obsoletes(self, tmp_path):
        repo = make_repo(tmp_path)
        regen.main(["--root", str(repo)])
        source = repo / ".claude" / "agents" / "rf-demo.md"
        source.write_text(AGENT.replace("1.2.3", "1.2.4"), encoding="utf-8")
        assert regen.main(["--root", str(repo), "--check"]) == 1


class TestDepotReel:
    def test_les_chatmodes_committes_sont_a_jour(self):
        """Le garde de la CI, joué ici : toute édition d'un agent doit être
        suivie d'une régénération dans le même commit."""
        assert regen.main(["--root", str(_ROOT), "--check"]) == 0

    def test_les_agents_portent_la_version_du_depot(self):
        """Ce dépôt ne publie pas de paquet : sa version vit dans VERSION, et
        c'est elle que ses agents portent. La changer sans eux fait échouer ici."""
        attendue = (_ROOT / "VERSION").read_text(encoding="utf-8").strip()
        assert regen.shared_version(_ROOT) == attendue
