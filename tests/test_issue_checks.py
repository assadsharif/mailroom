from pathlib import Path

import pytest

from mailroom.checks import check_footer, check_greeting, check_issue, check_links, check_preview, check_subject
from mailroom.issues import Issue

ROOT = Path(__file__).resolve().parents[1]
ISSUE_TEXT = (ROOT / "issues" / "issue-01.md").read_text(encoding="utf-8")


def replace_line(prefix: str, new: str | None) -> str:
    """Return the issue with the first line starting with `prefix` replaced, or removed if new is None."""
    lines = ISSUE_TEXT.splitlines()
    for index, line in enumerate(lines):
        if line.startswith(prefix):
            if new is None:
                del lines[index]
            else:
                lines[index] = new
            break
    return "\n".join(lines)


def test_the_real_issue_passes_every_check():
    assert check_issue(Issue.parse(ISSUE_TEXT)) == []


@pytest.mark.parametrize(
    ("subject_line", "expected_problems"),
    [
        ("Subject: The Steep Club opens Monday", 0),
        ("Subject: Your Steep Club box ships on Monday with new teas.", 0),
        ("Subject: Your Steep Club box ships on Monday with fresh teas", 1),
        ("Subject:", 1),
        ("Subject:    ", 1),
        (None, 1),
    ],
)
def test_subject_rule(subject_line, expected_problems):
    text = replace_line("Subject:", subject_line)
    assert len(check_subject(Issue.parse(text))) == expected_problems


def test_subject_of_exactly_50_characters_is_allowed():
    assert len("Your Steep Club box ships on Monday with new teas.") == 50


def test_subject_of_50_characters_with_surrounding_spaces_is_allowed():
    subject = "Your Steep Club box ships on Monday with new teas."
    text = replace_line("Subject:", f"Subject:  {subject}  ")
    assert len(check_subject(Issue.parse(text))) == 0


def test_a_subject_that_is_not_the_first_line_is_a_problem():
    text = "Preview: Your monthly tea box.\nSubject: The Steep Club opens Monday\n\nHi {{first_name}},\n"
    assert len(check_subject(Issue.parse(text))) == 1


def test_emoji_counts_as_python_len_counts():
    subject = "👍🏽 Thanks for joining"
    assert len(subject) == 21
    text = replace_line("Subject:", f"Subject: {subject}")
    assert check_subject(Issue.parse(text)) == []


@pytest.mark.parametrize(("preview_length", "expected_problems"), [(90, 0), (91, 1)])
def test_preview_rule(preview_length, expected_problems):
    text = replace_line("Preview:", "Preview: " + "p" * preview_length)
    assert len(check_preview(Issue.parse(text))) == expected_problems


def test_greeting_rule():
    text = ISSUE_TEXT.replace("{{first_name}}", "Friend")
    assert len(check_greeting(Issue.parse(text))) == 1


def test_two_links_is_a_problem():
    text = ISSUE_TEXT + "\n[Second](https://kettlebird.example/other)\n"
    assert len(check_links(Issue.parse(text))) == 1


def test_an_http_link_counts_and_is_a_problem():
    text = ISSUE_TEXT.replace("https://kettlebird.example/steep-club", "http://kettlebird.example/steep-club")
    problems = check_links(Issue.parse(text))
    assert len(problems) == 1
    assert "https" in problems[0]


def test_footer_needs_the_reason_line_and_the_unsubscribe_line():
    text = ISSUE_TEXT.replace("You're getting this because you joined the Kettlebird Tea waitlist.\n", "")
    assert len(check_footer(Issue.parse(text))) == 1


def test_no_footer_and_no_greeting_are_two_problems():
    text = ISSUE_TEXT.replace("{{first_name}}", "Friend")
    text = text.replace("You're getting this because", "Bye").replace("Unsubscribe: {{unsubscribe_url}}", "")
    assert len(check_issue(Issue.parse(text))) == 2
