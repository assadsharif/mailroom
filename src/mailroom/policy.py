"""The one copy of the recipient rule. Sending and the Claude Code guard both use it."""

PRACTICE_DOMAINS: tuple[str, ...] = ("example.com", "resend.dev")


def recipient_allowed(address: str) -> bool:
    _, _, domain = address.rpartition("@")
    return domain.lower() in PRACTICE_DOMAINS
