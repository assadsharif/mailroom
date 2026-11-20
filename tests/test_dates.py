from datetime import date

import pytest

from mailroom.dates import joined_within, next_send


def test_joined_on_21_october_counts_in_the_last_30_days():
    assert joined_within(date(2026, 10, 21), date(2026, 11, 20), 30)


def test_joined_on_20_october_does_not_count_in_the_last_30_days():
    assert not joined_within(date(2026, 10, 20), date(2026, 11, 20), 30)


@pytest.mark.parametrize(
    ("run_date", "expected"),
    [
        (date(2026, 11, 20), date(2026, 12, 7)),
        (date(2026, 12, 7), date(2027, 1, 4)),
        (date(2026, 12, 31), date(2027, 1, 4)),
    ],
)
def test_next_send_is_the_first_monday_of_the_next_month(run_date, expected):
    assert next_send(run_date) == expected
