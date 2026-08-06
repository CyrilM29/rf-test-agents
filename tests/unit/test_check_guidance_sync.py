"""Tests du garde de propagation des conventions CLAUDE.md → définitions
d'agents (`scripts/check_guidance_sync.py`).

Ce garde travaille sur le dépôt réel (chemins figés au niveau module) : les
tests vérifient donc l'état committé et la logique de détection, en
monkeypatchant les chemins pour les cas négatifs."""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "scripts"))

import check_guidance_sync as guard  # noqa: E402


class TestDepotReel:
    def test_conventions_portees_par_les_agents(self):
        """L'état committé doit être aligné : c'est ce que joue la CI."""
        assert guard.check() == []

    def test_toutes_les_conventions_suivies_existent_dans_claude_md(self):
        claude_md = (_ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        for num, anchor in guard._TRACKED:
            assert anchor in claude_md, "convention #%d absente" % num


class TestDetection:
    def _fake_repo(self, tmp_path, claude_md, agent_body):
        (tmp_path / ".claude" / "agents").mkdir(parents=True)
        (tmp_path / "CLAUDE.md").write_text(claude_md, encoding="utf-8")
        (tmp_path / ".claude" / "agents" / "rf-x.md").write_text(
            agent_body, encoding="utf-8")
        return tmp_path

    def _point_guard_at(self, monkeypatch, repo):
        monkeypatch.setattr(guard, "_CLAUDE_MD", repo / "CLAUDE.md")
        monkeypatch.setattr(guard, "_AGENTS_DIR", repo / ".claude" / "agents")

    def _full_claude_md(self):
        return "\n".join(anchor for _, anchor in guard._TRACKED)

    def _full_agent(self):
        return ("Sync note : resources/ ; time.sleep interdit ; "
                "mots de passe en Secret: sur la ligne de commande.")

    def test_repo_aligne_ne_signale_rien(self, tmp_path, monkeypatch):
        repo = self._fake_repo(tmp_path, self._full_claude_md(),
                               self._full_agent())
        self._point_guard_at(monkeypatch, repo)
        assert guard.check() == []

    def test_convention_reformulee_dans_claude_md(self, tmp_path, monkeypatch):
        amputé = self._full_claude_md().replace(
            "Never fabricate locators", "Ne jamais inventer de localisateur")
        repo = self._fake_repo(tmp_path, amputé, self._full_agent())
        self._point_guard_at(monkeypatch, repo)
        problems = guard.check()
        assert any("#4" in p for p in problems)

    def test_marqueur_perdu_par_un_agent(self, tmp_path, monkeypatch):
        repo = self._fake_repo(
            tmp_path, self._full_claude_md(),
            self._full_agent().replace("time.sleep", "attente"))
        self._point_guard_at(monkeypatch, repo)
        problems = guard.check()
        assert any("#2" in p and "rf-x.md" in p for p in problems)

    def test_note_de_synchronisation_perdue(self, tmp_path, monkeypatch):
        repo = self._fake_repo(
            tmp_path, self._full_claude_md(),
            self._full_agent().replace("Sync note", "Remarque"))
        self._point_guard_at(monkeypatch, repo)
        problems = guard.check()
        assert any("#8" in p for p in problems)

    def test_aucune_definition_d_agent(self, tmp_path, monkeypatch):
        (tmp_path / ".claude" / "agents").mkdir(parents=True)
        (tmp_path / "CLAUDE.md").write_text(self._full_claude_md(),
                                            encoding="utf-8")
        self._point_guard_at(monkeypatch, tmp_path)
        problems = guard.check()
        assert any("aucune définition d'agent" in p for p in problems)
