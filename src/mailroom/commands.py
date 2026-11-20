"""The command line. The only module that prints, and the only one that reads today's date."""

import argparse
import asyncio
import json
import sys
import time
from collections.abc import Callable
from datetime import date
from pathlib import Path
from typing import Any

import httpx

from mailroom.checks import check_path
from mailroom.dates import next_send
from mailroom.errors import MailroomError
from mailroom.guard import guard_decision
from mailroom.issues import Issue
from mailroom.send import build_plan, send_all
from mailroom.subscribers import (
    GROUPS,
    RowProblem,
    count_by_group,
    joined_since,
    meaning_problems,
    read_rows,
)

DEFAULT_SUBSCRIBERS = Path("data/subscribers.csv")


def _run_date(value: date | None) -> date:
    return value if value is not None else date.today()


def _print_problems(problems: list[RowProblem]) -> None:
    for problem in problems:
        print(f"row {problem.row}, {problem.field}: {problem.message}")


def cmd_subscribers(args: argparse.Namespace) -> int:
    subscribers, problems = read_rows(args.file)
    print(f"Total: {len(subscribers)}")
    counts = count_by_group(subscribers)
    for group in GROUPS:
        print(f"{group}: {counts.get(group, 0)}")
    if args.since_days is not None:
        recent = joined_since(subscribers, _run_date(args.run_date), args.since_days)
        print(f"Joined in the last {args.since_days} days: {len(recent)}")
    _print_problems(problems)
    return 1 if problems else 0


def cmd_next_send(args: argparse.Namespace) -> int:
    print(next_send(_run_date(args.run_date)).isoformat())
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    problems = check_path(args.file)
    if problems:
        for problem in problems:
            print(problem)
        return 1
    print("OK")
    return 0


def cmd_import(args: argparse.Namespace) -> int:
    run_date = _run_date(args.run_date)
    accepted, problems = read_rows(args.file)
    _print_problems(problems)
    rejected = len(problems)
    for subscriber in accepted:
        name = f"{subscriber.first_name} {subscriber.last_name}"
        reasons = meaning_problems(subscriber, run_date)
        if reasons:
            rejected += 1
            print(f"rejected {name}: {'; '.join(reasons)}")
        else:
            print(f"accepted {name}")
    return 1 if rejected else 0


def _message(response: httpx.Response) -> str:
    try:
        return str(response.json().get("message", response.text))
    except ValueError:
        return response.text


def cmd_send(args: argparse.Namespace) -> int:
    issue_problems = check_path(args.issue)
    if issue_problems:
        for problem in issue_problems:
            print(problem)
        print("Not sent: the issue fails its checks.")
        return 1
    subscribers, problems = read_rows(args.file)
    if problems:
        _print_problems(problems)
        return 1
    issue = Issue.from_path(args.issue)
    plan = build_plan(issue, subscribers, _run_date(args.run_date), slug=args.issue.stem)

    if args.dry_run:
        Path("outbox").mkdir(exist_ok=True)
        Path("outbox/plan.json").write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Dry run: {len(plan)} emails planned in outbox/plan.json. Nothing sent.")
        return 0

    started = time.perf_counter()
    try:
        responses = asyncio.run(send_all(plan, latency=args.latency, at_once=args.at_once))
    except httpx.ConnectError:
        raise MailroomError(
            "The practice server is not running. Start it in another terminal with: "
            "npx emulate@0.12.3 start --service resend"
        )
    elapsed = time.perf_counter() - started
    ok = sum(1 for response in responses if response.is_success)
    print(f"Sent {ok} of {len(plan)} in {elapsed:.1f} seconds.")
    for response in responses:
        if not response.is_success:
            print(f"failed {response.status_code}: {_message(response)}")
    return 0 if ok == len(plan) else 1


def cmd_guard(args: argparse.Namespace) -> int:
    try:
        payload: dict[str, Any] = json.load(sys.stdin)
    except json.JSONDecodeError:
        raise MailroomError("The guard expected a JSON tool call on standard input.")
    code, message = guard_decision(payload)
    if message:
        print(message, file=sys.stderr)
    return code


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="mailroom", description="Checks and sends the Steep Club newsletter.")
    commands = parser.add_subparsers(dest="command", required=True)

    sub = commands.add_parser("subscribers", help="count subscribers")
    sub.add_argument("--file", type=Path, default=DEFAULT_SUBSCRIBERS)
    sub.add_argument("--since-days", type=int)
    sub.add_argument("--run-date", type=date.fromisoformat)
    sub.set_defaults(handler=cmd_subscribers)

    nxt = commands.add_parser("next-send", help="the next send date")
    nxt.add_argument("--run-date", type=date.fromisoformat)
    nxt.set_defaults(handler=cmd_next_send)

    chk = commands.add_parser("check", help="check an issue against the rules")
    chk.add_argument("file", type=Path)
    chk.set_defaults(handler=cmd_check)

    imp = commands.add_parser("import", help="check a file of new sign-ups")
    imp.add_argument("file", type=Path)
    imp.add_argument("--run-date", type=date.fromisoformat)
    imp.set_defaults(handler=cmd_import)

    snd = commands.add_parser("send", help="send an issue to the practice server")
    snd.add_argument("issue", type=Path)
    snd.add_argument("--file", type=Path, default=DEFAULT_SUBSCRIBERS)
    snd.add_argument("--dry-run", action="store_true")
    snd.add_argument("--run-date", type=date.fromisoformat)
    snd.add_argument("--latency", type=float, default=0.0)
    snd.add_argument("--at-once", type=int, default=1)
    snd.set_defaults(handler=cmd_send)

    grd = commands.add_parser("guard", help="Claude Code hook: refuse non-practice recipients")
    grd.set_defaults(handler=cmd_guard)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    handler: Callable[[argparse.Namespace], int] = args.handler
    try:
        return handler(args)
    except MailroomError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2
