"""Tests unitaires du garde mécanique des conventions #1 (localisateurs) et
#2 (Sleep)."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

import check_conventions as guard  # noqa: E402


def make_repo(tmp_path: Path) -> Path:
    (tmp_path / "tests" / "robot" / "ui" / "web").mkdir(parents=True)
    (tmp_path / "resources" / "page_objects").mkdir(parents=True)
    return tmp_path


def write_suite(repo: Path, body: str) -> Path:
    suite = repo / "tests" / "robot" / "ui" / "web" / "s.robot"
    suite.write_text(body, encoding="utf-8")
    return suite


def write_resource(repo: Path, body: str) -> Path:
    resource = repo / "resources" / "page_objects" / "p.resource"
    resource.write_text(body, encoding="utf-8")
    return resource


CLEAN_SUITE = """*** Settings ***
Documentation     Générée depuis specs/x.md : on peut citer css=#exemple ici.
...               Suite de la doc, xpath=//aussi ignoré.
Resource          ../../../../resources/page_objects/p.resource

*** Test Cases ***
Connexion Nominale
    # commentaire avec css=#ignoré
    Open App And Log In    ${USER}
    Vérifier Le Tableau De Bord    timeout=10s
    Log    https://exemple.test/page
"""


class TestConventionUn:
    def test_suite_propre_passe(self, tmp_path):
        repo = make_repo(tmp_path)
        write_suite(repo, CLEAN_SUITE)
        assert guard.check(repo) == 0

    @pytest.mark.parametrize("cellule", [
        "css=#login-button",
        "xpath=//button[1]",
        "//div[@id='x']",
        "id=submit",
        "text=Se connecter",
        "form >> input.name",
    ])
    def test_localisateur_brut_dans_un_test_echoue(self, tmp_path, cellule):
        repo = make_repo(tmp_path)
        write_suite(repo, "*** Test Cases ***\nCas\n    Click    %s\n"
                    % cellule)
        assert guard.check(repo) == 1

    def test_localisateur_dans_variables_de_suite_echoue(self, tmp_path):
        repo = make_repo(tmp_path)
        write_suite(repo, "*** Variables ***\n"
                          "${LOC}    css=#interdit-en-suite\n")
        assert guard.check(repo) == 1

    def test_localisateur_dans_resource_autorise(self, tmp_path):
        repo = make_repo(tmp_path)
        write_resource(repo, "*** Variables ***\n"
                             "${LOGIN_BUTTON}    css=#login-button\n")
        assert guard.check(repo) == 0


class TestConventionDeux:
    def test_sleep_dans_un_test_echoue(self, tmp_path):
        repo = make_repo(tmp_path)
        write_suite(repo, "*** Test Cases ***\nCas\n    Sleep    2s\n")
        assert guard.check(repo) == 1

    def test_sleep_qualifie_dans_une_resource_echoue(self, tmp_path):
        repo = make_repo(tmp_path)
        write_resource(repo, "*** Keywords ***\nAttendre\n"
                             "    BuiltIn.Sleep    1s\n")
        assert guard.check(repo) == 1

    def test_wait_until_reste_autorise(self, tmp_path):
        repo = make_repo(tmp_path)
        write_resource(repo, "*** Keywords ***\nAttendre\n"
                             "    Wait Until Keyword Succeeds    5x    200ms"
                             "    Faire\n")
        assert guard.check(repo) == 0


class TestCiblage:
    def test_cible_explicite(self, tmp_path):
        repo = make_repo(tmp_path)
        suite = write_suite(repo, "*** Test Cases ***\nCas\n    Sleep    1s\n")
        assert guard.check(repo, [str(suite.relative_to(repo))]) == 1

    def test_workspace_vide_passe(self, tmp_path):
        repo = make_repo(tmp_path)
        assert guard.check(repo) == 0


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
