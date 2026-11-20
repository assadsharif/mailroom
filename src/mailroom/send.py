"""Building the plan and sending it to the practice server. Nothing here prints."""

import asyncio
import os
from datetime import date
from typing import Any

import httpx

from mailroom.errors import MailroomError
from mailroom.issues import Issue
from mailroom.policy import recipient_allowed
from mailroom.subscribers import Subscriber

COMPANY_ADDRESS = "12 Leaf Lane, Portland, OR 97201"
UNSUBSCRIBE_URL = "https://kettlebird.example/unsubscribe"
FROM_ADDRESS = "onboarding@resend.dev"
DEFAULT_URL = "http://localhost:4000"
PRACTICE_KEY = "re_practice"
RETRY_ATTEMPTS = 3
BACKOFF_SECONDS = 0.5


def server_url() -> str:
    return os.environ.get("RESEND_API_URL", DEFAULT_URL)


def api_key() -> str:
    return os.environ.get("RESEND_API_KEY", PRACTICE_KEY)


def require_localhost(url: str) -> None:
    host = httpx.URL(url).host
    if host not in ("localhost", "127.0.0.1"):
        raise MailroomError(f"Refusing to send to {host}. Sending works only against localhost.")


def build_plan(issue: Issue, subscribers: list[Subscriber], run_date: date, slug: str) -> list[dict[str, Any]]:
    """One entry per subscriber, with every placeholder filled in."""
    entries: list[dict[str, Any]] = []
    for subscriber in subscribers:
        if not recipient_allowed(subscriber.email):
            raise MailroomError(f"{subscriber.email} is not a practice address.")
        text = (
            issue.personalize(subscriber.first_name)
            .replace("{{company_address}}", COMPANY_ADDRESS)
            .replace("{{unsubscribe_url}}", UNSUBSCRIBE_URL)
        )
        entries.append({
            "to": subscriber.email,
            "subject": (issue.subject or "").strip(),
            "text": text,
            "idempotency_key": f"{slug}:{subscriber.email}",
            "run_date": run_date.isoformat(),
        })
    return entries


async def send_one(
    client: httpx.AsyncClient,
    entry: dict[str, Any],
    semaphore: asyncio.Semaphore,
    latency: float,
) -> httpx.Response:
    """Send one email. Retry only network errors, 429 and 5xx, never a 4xx."""
    async with semaphore:
        for attempt in range(1, RETRY_ATTEMPTS + 1):
            await asyncio.sleep(latency)
            try:
                response = await client.post(
                    "/emails",
                    json={"from": FROM_ADDRESS, "to": [entry["to"]], "subject": entry["subject"], "text": entry["text"]},
                    headers={"Idempotency-Key": entry["idempotency_key"]},
                )
            except (httpx.ConnectError, httpx.TimeoutException):
                if attempt == RETRY_ATTEMPTS:
                    raise
            else:
                retryable = response.status_code == 429 or response.status_code >= 500
                if not retryable or attempt == RETRY_ATTEMPTS:
                    return response
            await asyncio.sleep(BACKOFF_SECONDS * 2 ** (attempt - 1))
    raise AssertionError("unreachable: every attempt returns or raises")


async def send_all(plan: list[dict[str, Any]], latency: float = 0.0, at_once: int = 1) -> list[httpx.Response]:
    url = server_url()
    require_localhost(url)
    semaphore = asyncio.Semaphore(at_once)
    headers = {"Authorization": f"Bearer {api_key()}"}
    async with httpx.AsyncClient(base_url=url, headers=headers, timeout=10.0) as client:
        results = await asyncio.gather(*(send_one(client, entry, semaphore, latency) for entry in plan))
    return list(results)
