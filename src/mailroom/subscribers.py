"""Reading subscribers and sign-ups. Bad rows are reported with their row number, never fatal."""

import csv
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, ValidationError

from mailroom.dates import joined_within
from mailroom.errors import MailroomError

GROUPS: tuple[str, ...] = ("tea-curious", "gift-buyers", "daily-drinkers")
REQUIRED_COLUMNS = {"first_name", "last_name", "email", "group", "joined_on", "consent"}


class SignUp(BaseModel):
    """The shape of one row. Data from outside is checked here before any code uses it."""

    first_name: str = Field(min_length=1)
    last_name: str = Field(min_length=1)
    email: EmailStr
    group: Literal["tea-curious", "gift-buyers", "daily-drinkers"]
    joined_on: date
    consent: str = Field(min_length=1)


@dataclass(frozen=True)
class Subscriber:
    first_name: str
    last_name: str
    email: str
    group: str
    joined_on: date
    consent: str


@dataclass(frozen=True)
class RowProblem:
    row: int
    field: str
    message: str


def read_rows(path: Path) -> tuple[list[Subscriber], list[RowProblem]]:
    """Return the valid subscribers and every problem found, each with its row number."""
    if not path.exists():
        raise MailroomError(f"There is no file at {path}.")
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
        if missing:
            raise MailroomError(f"{path} is missing columns: {', '.join(sorted(missing))}.")
        accepted: list[Subscriber] = []
        problems: list[RowProblem] = []
        for row_number, row in enumerate(reader, start=2):
            try:
                signup = SignUp.model_validate(row)
            except ValidationError as error:
                for detail in error.errors():
                    field = str(detail["loc"][0]) if detail["loc"] else "row"
                    problems.append(RowProblem(row_number, field, detail["msg"]))
                continue
            accepted.append(Subscriber(**signup.model_dump()))
    return accepted, problems


def count_by_group(subscribers: list[Subscriber]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for subscriber in subscribers:
        counts[subscriber.group] = counts.get(subscriber.group, 0) + 1
    return counts


def joined_since(subscribers: list[Subscriber], run_date: date, days: int) -> list[Subscriber]:
    return [s for s in subscribers if joined_within(s.joined_on, run_date, days)]


def joined_from(subscribers: list[Subscriber], since: date) -> list[Subscriber]:
    """Subscribers who joined on or after `since`."""
    return [s for s in subscribers if s.joined_on >= since]


def meaning_problems(subscriber: Subscriber, run_date: date) -> list[str]:
    """Our own rules, which a shape check cannot know."""
    problems: list[str] = []
    if not subscriber.email.lower().endswith("@example.com"):
        problems.append("not an @example.com address")
    if subscriber.joined_on > run_date:
        problems.append("joined after the run date")
    return problems
