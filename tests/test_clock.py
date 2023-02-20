from easyflake.sequence import ScaledClock
from datetime import datetime
from freezegun import freeze_time


def test_current():
    with freeze_time("2020-01-01 00:00:00"):
        clock = ScaledClock(3, datetime(2020, 1, 1).timestamp())
        with freeze_time("2020-01-01 00:01:01.12345"):
            now = clock.current()
    assert now == 61123


def test_get_full_timestamp():
    with freeze_time("2020-01-01 00:00:00"):
        clock = ScaledClock(3, 0)
        with freeze_time("2023-01-01 00:00:00.123"):
            now = clock.current()
    assert clock.get_elapsed_time(now) == 1672531200_123
