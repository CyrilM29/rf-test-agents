"""Fil de reprise : lisible par un autre agent, sans rejeu ni permission implicite."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import agent_handover as handover
import agent_journal as journal

MISSION = {"target": "lab-1", "mode": "explore", "invariant": "Le panier revient a son etat initial"}


def open_mission(root, mission="mission-1", **extra):
    return handover.record(root, mission, "mission", "planner", "Explorer le panier", **MISSION, **extra)


def run(capsys, *argv):
    code = handover.main(list(argv))
    captured = capsys.readouterr()
    return code, captured.out, captured.err


def test_round_trip_names_the_last_intended_move(tmp_path):
    open_mission(tmp_path)
    handover.record(tmp_path, "mission-1", "step", "planner", "Connexion prouvee sur lab-1")
    handover.record(tmp_path, "mission-1", "finding", "planner", "Le bouton porte data-test=add",
                    refs=["specs/evidence/panier.json"])
    handover.record(tmp_path, "mission-1", "next", "planner", "Vider le panier puis relire",
                    budget_used={"tool_calls": 12})
    summary = handover.resume(tmp_path, "mission-1")
    assert summary["state"] == "resume_after_reperception"
    assert summary["last_next"]["seq"] == 4 and not summary["last_next"]["followed"]
    assert summary["budget_used"] == {"tool_calls": 12}
    assert [item["seq"] for item in summary["trail"]] == [1, 2, 3, 4]
    text = handover.render_markdown(summary)
    assert "Le panier revient a son etat initial" in text and "re-perceive" in text
    assert "specs/evidence/panier.json" in text


def test_a_move_followed_by_later_entries_is_flagged(tmp_path):
    open_mission(tmp_path)
    handover.record(tmp_path, "mission-1", "next", "planner", "Ouvrir la fiche")
    handover.record(tmp_path, "mission-1", "step", "planner", "Fiche ouverte")
    assert handover.resume(tmp_path, "mission-1")["last_next"]["followed"] is True


@pytest.mark.parametrize("kind", ["step", "finding", "next", "closed"])
def test_first_entry_must_be_the_mission(tmp_path, kind):
    with pytest.raises(ValueError, match="mission"):
        handover.record(tmp_path, "m", kind, "planner", "x")
    assert not list((tmp_path / "m" / "handover").glob("*.json"))


@pytest.mark.parametrize("fields", [
    {"target": "lab-1", "mode": "explore"},
    {"target": "lab-1", "mode": "write_all", "invariant": "i"},
    {"target": "../lab", "mode": "explore", "invariant": "i"},
])
def test_mission_needs_target_mode_and_invariant(tmp_path, fields):
    with pytest.raises(ValueError):
        handover.record(tmp_path, "m", "mission", "planner", "x", **fields)


def test_a_second_mission_entry_is_refused(tmp_path):
    open_mission(tmp_path)
    with pytest.raises(ValueError, match="first entry"):
        open_mission(tmp_path)


@pytest.mark.parametrize("text", [
    "SAP_PASSWORD: Secret:hunter2",
    "password=hunter2",
    "api_key = 0123456789",
    "Authorization: Basic ZGV2Og==",
    "Bearer eyJhbGciOiJIUzI1NiJ9abc123",
    "http://developer:hunter2@localhost:50000",
    "-----BEGIN RSA PRIVATE KEY-----",
])
def test_credentials_are_refused_and_nothing_is_written(tmp_path, text):
    open_mission(tmp_path)
    with pytest.raises(ValueError, match="credential"):
        handover.record(tmp_path, "mission-1", "finding", "planner", text)
    assert len(handover.read_trail(tmp_path, "mission-1")) == 1


@pytest.mark.parametrize("text", [
    "Mot de passe passe par la variable SAP_PASSWORD en ligne de commande",
    "Tokens consommes : 689 462",
    "Bearer authentication accepted by the gateway",
    "https://localhost:50101/sap/bc/ui2/flp repond en 200",
])
def test_innocent_mentions_pass_the_screen(tmp_path, text):
    open_mission(tmp_path)
    assert handover.record(tmp_path, "mission-1", "finding", "planner", text)["seq"] == 2


@pytest.mark.parametrize("ref", [
    "C:/results/x.json", "/etc/hosts", "..\\x", "../outside.json", "https://host/x", "",
])
def test_references_stay_workspace_relative(tmp_path, ref):
    open_mission(tmp_path)
    with pytest.raises(ValueError, match="reference"):
        handover.record(tmp_path, "mission-1", "finding", "planner", "x", refs=[ref])


@pytest.mark.parametrize("budget", [{"tool_calls": -1}, {"calls": 3}, {"attempts": True}])
def test_budget_used_is_strict(tmp_path, budget):
    open_mission(tmp_path)
    with pytest.raises(ValueError, match="budget_used"):
        handover.record(tmp_path, "mission-1", "step", "planner", "x", budget_used=budget)


def test_oversized_text_is_refused(tmp_path):
    open_mission(tmp_path)
    with pytest.raises(ValueError, match="split"):
        handover.record(tmp_path, "mission-1", "finding", "planner", "x" * (handover.MAX_TEXT + 1))


def test_missing_entry_stops_resumption(tmp_path, capsys):
    open_mission(tmp_path)
    handover.record(tmp_path, "mission-1", "step", "planner", "a")
    handover.record(tmp_path, "mission-1", "finding", "planner", "b")
    (tmp_path / "mission-1/handover/0002.json").unlink()
    summary = handover.resume(tmp_path, "mission-1")
    assert summary["state"] == "stop" and "0002" in summary["reason"]
    assert run(capsys, "resume", "mission-1", "--root", str(tmp_path))[0] == 2


def test_tampered_entry_stops_resumption(tmp_path):
    open_mission(tmp_path)
    handover.record(tmp_path, "mission-1", "step", "planner", "a")
    path = tmp_path / "mission-1/handover/0002.json"
    path.write_text(path.read_text(encoding="utf-8").replace('"seq": 2', '"seq": 5'), encoding="utf-8")
    assert handover.resume(tmp_path, "mission-1")["state"] == "stop"


def test_unexpected_file_stops_resumption(tmp_path):
    open_mission(tmp_path)
    (tmp_path / "mission-1/handover/notes.md").write_text("brouillon", encoding="utf-8")
    assert "notes.md" in handover.resume(tmp_path, "mission-1")["reason"]


def test_leftover_lock_stops_and_is_never_removed(tmp_path, capsys):
    open_mission(tmp_path)
    lock = tmp_path / "mission-1/handover/handover.lock"
    lock.touch()
    assert run(capsys, "resume", "mission-1", "--root", str(tmp_path))[0] == 2
    with pytest.raises(FileExistsError):
        handover.record(tmp_path, "mission-1", "step", "planner", "a")
    assert lock.exists()


def test_closed_mission_accepts_no_further_entry(tmp_path, capsys):
    open_mission(tmp_path)
    handover.record(tmp_path, "mission-1", "closed", "planner", "Plan livre")
    with pytest.raises(ValueError, match="closed"):
        handover.record(tmp_path, "mission-1", "step", "planner", "a")
    assert run(capsys, "resume", "mission-1", "--root", str(tmp_path))[0] == 1


def test_open_questions_are_those_without_a_decision(tmp_path):
    open_mission(tmp_path)
    handover.record(tmp_path, "mission-1", "question", "planner", "Cible A4H ou 2023 ?")
    handover.record(tmp_path, "mission-1", "question", "planner", "Garder les donnees ?")
    handover.record(tmp_path, "mission-1", "decision", "planner", "A4H, decide par l'utilisateur", resolves=2)
    summary = handover.resume(tmp_path, "mission-1")
    assert summary["open_questions"] == [3]
    text = handover.render_markdown(summary)
    assert "(answered by #4)" in text and "(open)" in text
    with pytest.raises(ValueError, match="question"):
        handover.record(tmp_path, "mission-1", "decision", "planner", "x", resolves=1)


def test_dispatched_write_blocks_until_reconciled(tmp_path, capsys):
    open_mission(tmp_path)
    journal.record(tmp_path, "mission-1", "create-order", "planned")
    journal.record(tmp_path, "mission-1", "create-order", "sent")
    summary = handover.resume(tmp_path, "mission-1")
    assert summary["state"] == "reconcile_first"
    assert summary["journal"] == [{"action": "create-order", "phases": ["planned", "sent"],
                                   "next_action": "reconcile_before_retry"}]
    assert run(capsys, "resume", "mission-1", "--root", str(tmp_path))[0] == 3
    journal.record(tmp_path, "mission-1", "create-order", "confirmed", "proof-1")
    summary = handover.resume(tmp_path, "mission-1")
    assert summary["state"] == "resume_after_reperception"
    assert summary["journal"][0]["next_action"] == "do_not_replay"


def test_closing_does_not_hide_a_pending_write(tmp_path):
    open_mission(tmp_path)
    journal.record(tmp_path, "mission-1", "create-order", "planned")
    journal.record(tmp_path, "mission-1", "create-order", "sent")
    handover.record(tmp_path, "mission-1", "closed", "planner", "Termine")
    assert handover.resume(tmp_path, "mission-1")["state"] == "reconcile_first"


def test_journal_lock_stops_resumption(tmp_path):
    open_mission(tmp_path)
    journal.record(tmp_path, "mission-1", "create-order", "planned")
    (tmp_path / "mission-1/create-order.lock").touch()
    assert handover.resume(tmp_path, "mission-1")["state"] == "stop"


def test_journal_without_trail_is_still_reported(tmp_path, capsys):
    journal.record(tmp_path, "mission-1", "create-order", "planned")
    summary = handover.resume(tmp_path, "mission-1")
    assert summary["state"] == "no_trail"
    assert summary["journal"][0]["next_action"] == "authorization_required"
    assert run(capsys, "resume", "mission-1", "--root", str(tmp_path))[0] == 1


def test_trail_must_agree_with_its_handoff_sidecar(tmp_path):
    root = tmp_path / "results/agent_runs"
    (tmp_path / "specs").mkdir()
    sidecar = tmp_path / "specs/panier.handoff.json"
    sidecar.write_text(json.dumps({"mission_id": "mission-1", "target": "lab-2", "mode": "explore"}),
                       encoding="utf-8")
    open_mission(root, handoff="specs/panier.handoff.json")
    summary = handover.resume(root, "mission-1", tmp_path)
    assert summary["state"] == "stop" and "target" in summary["reason"]
    sidecar.write_text(json.dumps({"mission_id": "mission-1", "target": "lab-1", "mode": "explore"}),
                       encoding="utf-8")
    assert handover.resume(root, "mission-1", tmp_path)["state"] == "resume_after_reperception"


def test_missing_handoff_sidecar_is_only_a_warning(tmp_path):
    root = tmp_path / "results/agent_runs"
    open_mission(root, handoff="specs/pas-encore.handoff.json")
    summary = handover.resume(root, "mission-1", tmp_path)
    assert summary["state"] == "resume_after_reperception" and summary["warnings"]


def test_entry_written_by_hand_is_accepted(tmp_path):
    open_mission(tmp_path)
    manual = {"schema_version": 1, "mission_id": "mission-1", "seq": 2, "agent": "planner",
              "kind": "finding", "timestamp": "2026-09-26", "text": "Relevé écrit sans shell, accents compris"}
    (tmp_path / "mission-1/handover/0002.json").write_text(
        "\ufeff" + json.dumps(manual, ensure_ascii=False), encoding="utf-8")
    assert handover.read_trail(tmp_path, "mission-1")[1]["text"].startswith("Relevé")
    assert handover.record(tmp_path, "mission-1", "next", "planner", "Suite")["seq"] == 3


def test_entries_are_written_with_lf_and_utf8(tmp_path):
    open_mission(tmp_path)
    handover.record(tmp_path, "mission-1", "finding", "planner", "Écart relevé : 3 lignes")
    raw = (tmp_path / "mission-1/handover/0002.json").read_bytes()
    assert b"\r\n" not in raw and "Écart".encode() in raw


def test_cli_json_output_carries_the_rules(tmp_path, capsys):
    open_mission(tmp_path)
    code, out, _ = run(capsys, "resume", "mission-1", "--root", str(tmp_path), "--format", "json",
                       "--workspace", str(tmp_path))
    data = json.loads(out)
    assert code == 0 and data["state"] == "resume_after_reperception" and len(data["rules"]) == 6


def test_cli_records_from_a_text_file(tmp_path, capsys):
    open_mission(tmp_path)
    note = tmp_path / "note.txt"
    note.write_text("Trois critères relevés\nsur deux lignes", encoding="utf-8")
    code, out, _ = run(capsys, "record", "mission-1", "--kind", "finding", "--agent", "planner",
                       "--text-file", str(note), "--tool-calls", "7", "--root", str(tmp_path))
    assert code == 0 and json.loads(out) == {"recorded": 2, "kind": "finding"}
    assert handover.resume(tmp_path, "mission-1")["budget_used"] == {"tool_calls": 7}


def test_cli_refusal_does_not_echo_the_secret(tmp_path, capsys):
    open_mission(tmp_path)
    code, out, err = run(capsys, "record", "mission-1", "--kind", "finding", "--agent", "planner",
                         "--text", "password=hunter2", "--root", str(tmp_path))
    assert code == 2 and "hunter2" not in out + err and "credential" in err


def test_no_trail_means_nothing_to_resume(tmp_path, capsys):
    assert run(capsys, "resume", "mission-1", "--root", str(tmp_path))[0] == 1
