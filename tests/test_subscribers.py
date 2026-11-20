from datetime import date
from pathlib import Path

import pytest

from mailroom.errors import MailroomError
from mailroom.subscribers import count_by_group, joined_since, meaning_problems, read_rows

ROOT = Path(__file__).resolve().parents[1]
SUBSCRIBERS = ROOT / "data" / "subscribers.csv"
NEW_SIGNUPS = ROOT / "data" / "new-signups.csv"


def test_there_are_24_subscribers():
    subscribers, problems = read_rows(SUBSCRIBERS)
    assert len(subscribers) == 24
    assert problems == []


@pytest.mark.parametrize("group", ["tea-curious", "gift-buyers", "daily-drinkers"])
def test_each_group_has_8_subscribers(group):
    subscribers, _ = read_rows(SUBSCRIBERS)
    assert count_by_group(subscribers)[group] == 8


def test_seven_subscribers_joined_in_the_last_30_days():
    subscribers, _ = read_rows(SUBSCRIBERS)
    assert len(joined_since(subscribers, date(2026, 11, 20), 30)) == 7


def test_a_bad_row_is_reported_with_its_row_number_not_fatal(tmp_path):
    path = tmp_path / "subs.csv"
    path.write_text(
        "first_name,last_name,email,group,joined_on,consent\n"
        "Ada,Lovelace,ada@example.com,tea-curious,2026-11-01,waitlist form\n"
        "Bob,Stone,bob@example.com,tea-curious,2026-02-30,waitlist form\n",
        encoding="utf-8",
    )
    subscribers, problems = read_rows(path)
    assert len(subscribers) == 1
    assert any(p.row == 3 and p.field == "joined_on" for p in problems)


def test_a_missing_file_is_one_plain_error(tmp_path):
    with pytest.raises(MailroomError):
        read_rows(tmp_path / "nope.csv")


def test_wrong_columns_stop_with_a_plain_error(tmp_path):
    path = tmp_path / "wrong.csv"
    path.write_text("name,mail\nAda,ada@example.com\n", encoding="utf-8")
    with pytest.raises(MailroomError, match="missing columns"):
        read_rows(path)


def test_new_signups_pass_the_shape_check_for_four_rows():
    accepted, problems = read_rows(NEW_SIGNUPS)
    assert {s.first_name for s in accepted} == {"Maria", "Sara", "Tom", "Ines"}
    assert {p.row for p in problems} == {3, 4, 5, 6}


def test_our_own_rules_reject_sara_and_tom():
    accepted, _ = read_rows(NEW_SIGNUPS)
    by_name = {s.first_name: s for s in accepted}
    run = date(2026, 11, 20)
    assert meaning_problems(by_name["Sara"], run)
    assert meaning_problems(by_name["Tom"], run)
    assert meaning_problems(by_name["Maria"], run) == []
    assert meaning_problems(by_name["Ines"], run) == []
