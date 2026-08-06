"""Tests unitaires du garde de provenance specs/ <-> tests/robot/."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

import check_spec_sync as guard  # noqa: E402


SUITE_TEMPLATE = """*** Settings ***
Documentation     Suite de démonstration.

*** Test Cases ***
Un Scénario
    Log    ok
"""


def make_repo(tmp_path: Path, spec_text: str = "# Plan\n\nContenu.\n") -> Path:
    (tmp_path / "specs").mkdir()
    (tmp_path / "specs" / "plan.md").write_text(spec_text, encoding="utf-8")
    suite_dir = tmp_path / "tests" / "robot" / "ui" / "web"
    suite_dir.mkdir(parents=True)
    (suite_dir / "plan.robot").write_text(SUITE_TEMPLATE, encoding="utf-8")
    return tmp_path


def stamp(repo: Path) -> None:
    assert guard.stamp(repo, "tests/robot/ui/web/plan.robot",
                       "specs/plan.md") == 0


class TestDigest:
    def test_crlf_et_lf_donnent_le_meme_hash(self, tmp_path: Path):
        lf = tmp_path / "lf.md"
        crlf = tmp_path / "crlf.md"
        lf.write_bytes(b"# Plan\nligne\n")
        crlf.write_bytes(b"# Plan\r\nligne\r\n")
        assert guard.spec_digest(lf) == guard.spec_digest(crlf)


class TestStamp:
    def test_insere_le_marqueur_sous_documentation_avec_date(self, tmp_path):
        repo = make_repo(tmp_path)
        stamp(repo)
        text = (repo / "tests/robot/ui/web/plan.robot").read_text(
            encoding="utf-8")
        match = guard.MARKER.search(text)
        assert match, text
        assert match.group("spec") == "specs/plan.md"
        assert match.group("date")  # la date de génération est présente
        # le marqueur est une ligne de continuation de la Documentation
        assert text.splitlines()[2].lstrip().startswith("...")

    def test_restamp_rafraichit_sans_dupliquer(self, tmp_path):
        repo = make_repo(tmp_path)
        stamp(repo)
        (repo / "specs" / "plan.md").write_text("# Plan\n\nChangé.\n",
                                                encoding="utf-8")
        stamp(repo)
        text = (repo / "tests/robot/ui/web/plan.robot").read_text(
            encoding="utf-8")
        assert len(guard.MARKER.findall(text)) == 1
        assert guard.check(repo) == 0

    def test_sans_ligne_documentation_echoue(self, tmp_path):
        repo = make_repo(tmp_path)
        suite = repo / "tests/robot/ui/web/plan.robot"
        suite.write_text("*** Test Cases ***\nCas\n    Log    ok\n",
                         encoding="utf-8")
        assert guard.stamp(repo, "tests/robot/ui/web/plan.robot",
                           "specs/plan.md") == 1


class TestCheck:
    def test_suite_en_phase(self, tmp_path):
        repo = make_repo(tmp_path)
        stamp(repo)
        assert guard.check(repo) == 0

    def test_spec_modifiee_sans_regeneration(self, tmp_path):
        repo = make_repo(tmp_path)
        stamp(repo)
        (repo / "specs" / "plan.md").write_text("# Plan\n\nDérive.\n",
                                                encoding="utf-8")
        assert guard.check(repo) == 1

    def test_marqueur_vers_spec_disparue(self, tmp_path):
        repo = make_repo(tmp_path)
        stamp(repo)
        (repo / "specs" / "plan.md").unlink()
        assert guard.check(repo) == 1

    def test_marqueur_historique_sans_date_reste_valide(self, tmp_path):
        repo = make_repo(tmp_path)
        digest = guard.spec_digest(repo / "specs" / "plan.md")
        suite = repo / "tests/robot/ui/web/plan.robot"
        suite.write_text(
            "*** Settings ***\n"
            "Documentation     Suite.\n"
            "...               Spec: specs/plan.md (sha256:%s)\n" % digest,
            encoding="utf-8")
        assert guard.check(repo) == 0

    def test_spec_sans_suite_est_informatif(self, tmp_path):
        repo = make_repo(tmp_path)
        assert guard.check(repo) == 0


class TestSpecPerimee:
    STALE_SPEC = ("# Plan\n\n"
                  "> **Statut : PÉRIMÉE (2026-07-24)**, le flux a changé ; "
                  "re-explorer via /rf-plan.\n\nContenu.\n")

    def test_marqueur_perimee_bloque(self, tmp_path):
        repo = make_repo(tmp_path, spec_text=self.STALE_SPEC)
        stamp(repo)
        assert guard.check(repo) == 1

    def test_readme_et_couverture_exemptes(self, tmp_path):
        repo = make_repo(tmp_path)
        stamp(repo)
        for name in ("README.md", "couverture-proposee.md"):
            (repo / "specs" / name).write_text(self.STALE_SPEC,
                                               encoding="utf-8")
        assert guard.check(repo) == 0

    def test_marqueur_retire_debloque(self, tmp_path):
        repo = make_repo(tmp_path, spec_text=self.STALE_SPEC)
        stamp(repo)
        (repo / "specs" / "plan.md").write_text(
            self.STALE_SPEC.replace(
                "> **Statut : PÉRIMÉE (2026-07-24)**, le flux a changé ; "
                "re-explorer via /rf-plan.\n\n", ""),
            encoding="utf-8")
        # le retrait du marqueur change le hash : re-stamp requis (voulu)
        assert guard.check(repo) == 1
        stamp(repo)
        assert guard.check(repo) == 0


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
