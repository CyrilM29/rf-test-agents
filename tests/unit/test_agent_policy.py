"""L'outil on/off écrit ce que le hook sait lire, et son état dit la vérité."""
import importlib.util
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "agent_policy.py"
SPEC = importlib.util.spec_from_file_location("agent_policy_under_test", SCRIPT)
outil = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(outil)


def test_on_writes_a_file_the_hook_reads_as_autonomous(tmp_path):
    fichier = tmp_path / ".claude" / "agent-policy.local.json"
    outil.activer(fichier)
    assert not fichier.read_bytes().startswith(b"\xef\xbb\xbf"), "BOM : le hook lirait confirm"
    assert outil.load_policy({}, fichier) == "autonomous"
    assert "Politique : autonomous (fichier" in outil.etat({}, fichier)


def test_off_returns_to_confirmation_even_when_already_off(tmp_path):
    fichier = tmp_path / "agent-policy.local.json"
    outil.activer(fichier)
    outil.desactiver(fichier)
    outil.desactiver(fichier)
    assert not fichier.exists()
    assert outil.etat({}, fichier).startswith("Politique : confirm (aucun réglage local)")


def test_status_names_the_environment_override_and_read_only(tmp_path):
    fichier = tmp_path / "agent-policy.local.json"
    outil.activer(fichier)
    texte = outil.etat({"RF_AGENT_POLICY": "confirm", "RF_AGENT_READ_ONLY": "1"}, fichier)
    assert "LECTURE SEULE" in texte
    assert "Politique : confirm (variable RF_AGENT_POLICY='confirm'" in texte


def test_status_warns_about_a_file_written_with_a_bom(tmp_path):
    fichier = tmp_path / "agent-policy.local.json"
    fichier.write_bytes(b'\xef\xbb\xbf{"policy": "autonomous"}')
    texte = outil.etat({}, fichier)
    assert texte.startswith("Politique : confirm")
    assert "illisible ou inconnu" in texte


def test_explicit_confirm_file_is_not_reported_as_unreadable(tmp_path):
    fichier = tmp_path / "agent-policy.local.json"
    fichier.write_text('{"policy": "confirm"}', encoding="utf-8")
    assert "illisible" not in outil.etat({}, fichier)


def test_cli_status_runs_from_a_foreign_working_directory(tmp_path):
    result = subprocess.run([sys.executable, str(SCRIPT), "status"], cwd=tmp_path,
                            capture_output=True, text=True, encoding="utf-8", check=False)
    assert result.returncode == 0
    assert result.stdout.startswith(("Politique : ", "Mode LECTURE SEULE"))
