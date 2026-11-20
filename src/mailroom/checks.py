"""The rules in docs/email-rules.md, as code. Each check returns a list of problems."""

from pathlib import Path

from mailroom.issues import ANY_LINK, Issue

SUBJECT_MAX = 50
PREVIEW_MAX = 90


def check_subject(issue: Issue) -> list[str]:
    if issue.subject is None:
        return ["missing: no Subject line"]
    text = issue.subject.strip()
    if not text:
        return ["subject is empty"]
    if len(text) > SUBJECT_MAX:
        return [f"subject is {len(text)} characters; the limit is {SUBJECT_MAX}"]
    return []


def check_preview(issue: Issue) -> list[str]:
    if issue.preview is None:
        return ["missing: no Preview line"]
    if len(issue.preview) > PREVIEW_MAX:
        return [f"preview is {len(issue.preview)} characters; the limit is {PREVIEW_MAX}"]
    return []


def check_greeting(issue: Issue) -> list[str]:
    if "{{first_name}}" not in issue.body:
        return ["no {{first_name}} greeting in the body"]
    return []


def check_links(issue: Issue) -> list[str]:
    problems: list[str] = []
    links = ANY_LINK.findall(issue.body)
    if len(links) != 1:
        problems.append(f"expected exactly one main link, found {len(links)}")
    for link in links:
        if link.startswith("http://"):
            problems.append(f"link must use https: {link}")
    return problems


def check_footer(issue: Issue) -> list[str]:
    lines = issue.body.splitlines()
    problems: list[str] = []
    if not any(line.startswith("You're getting this because") for line in lines):
        problems.append("footer is missing the line starting \"You're getting this because\"")
    if not any("Unsubscribe: {{unsubscribe_url}}" in line for line in lines):
        problems.append("footer is missing \"Unsubscribe: {{unsubscribe_url}}\"")
    return problems


def check_issue(issue: Issue) -> list[str]:
    return (
        check_subject(issue)
        + check_preview(issue)
        + check_greeting(issue)
        + check_links(issue)
        + check_footer(issue)
    )


def check_path(path: Path) -> list[str]:
    return check_issue(Issue.from_path(path))
