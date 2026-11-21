import json
from datetime import date
from pathlib import Path

from mailroom.commands import main
from mailroom.issues import Issue
from mailroom.send import build_plan
from mailroom.subscribers import read_rows

ROOT = Path(__file__).resolve().parents[1]
SUBSCRIBERS = ROOT / "data" / "subscribers.csv"
ISSUE = ROOT / "issues" / "issue-01.md"


def test_plan_has_one_entry_per_subscriber_and_fills_placeholders():
    subscribers, _ = read_rows(SUBSCRIBERS)
    plan = build_plan(Issue.from_path(ISSUE), subscribers, date(2026, 12, 7), slug="issue-01")
    assert len(plan) == 24
    assert plan[0]["to"] == "ayesha.khan@example.com"
    assert plan[0]["text"].startswith("Hi Ayesha,")
    assert "{{" not in plan[0]["text"]


def test_subscribers_command_prints_total_and_recent(capsys):
    code = main(["subscribers", "--file", str(SUBSCRIBERS), "--since-days", "30", "--run-date", "2026-11-20"])
    out = capsys.readouterr().out
    assert code == 0
    assert "Total: 24" in out
    assert "Joined in the last 30 days: 7" in out


def test_subscribers_command_counts_from_an_exact_date(capsys):
    code = main(["subscribers", "--file", str(SUBSCRIBERS), "--since", "2026-10-01"])
    out = capsys.readouterr().out
    assert code == 0
    assert "Joined since 2026-10-01: 12" in out


def test_next_send_command(capsys):
    main(["next-send", "--run-date", "2026-11-20"])
    assert capsys.readouterr().out.strip() == "2026-12-07"


def test_import_command_accepts_maria_and_ines(capsys):
    main(["import", str(ROOT / "data" / "new-signups.csv"), "--run-date", "2026-11-20"])
    out = capsys.readouterr().out
    assert "accepted Maria Lopez" in out
    assert "accepted Ines Costa" in out
    assert "rejected Sara Ali" in out
    assert "rejected Tom Lee" in out


def test_dry_run_writes_the_plan_and_sends_nothing(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    code = main(["send", str(ISSUE), "--dry-run", "--run-date", "2026-12-07", "--file", str(SUBSCRIBERS)])
    assert code == 0
    plan = json.loads((tmp_path / "outbox" / "plan.json").read_text(encoding="utf-8"))
    assert len(plan) == 24


def test_an_issue_that_fails_its_checks_writes_no_plan(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    bad = tmp_path / "bad.md"
    bad.write_text(ISSUE.read_text(encoding="utf-8").replace("https://", "http://"), encoding="utf-8")
    code = main(["send", str(bad), "--dry-run", "--file", str(SUBSCRIBERS)])
    assert code == 1
    assert not (tmp_path / "outbox" / "plan.json").exists()
