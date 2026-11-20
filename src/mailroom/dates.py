"""Date logic. Nothing here reads today's date: the run date is always passed in."""

from datetime import date, timedelta


def joined_within(joined: date, run_date: date, days: int) -> bool:
    """True if `joined` falls in the last `days` days, counting the run date's window inclusively."""
    start = run_date - timedelta(days=days)
    return start <= joined <= run_date


def first_monday(year: int, month: int) -> date:
    """The first Monday of the given month."""
    first = date(year, month, 1)
    offset = (0 - first.weekday()) % 7
    return first + timedelta(days=offset)


def next_send(run_date: date) -> date:
    """The first Monday of the month after the run date's month."""
    if run_date.month == 12:
        return first_monday(run_date.year + 1, 1)
    return first_monday(run_date.year, run_date.month + 1)
