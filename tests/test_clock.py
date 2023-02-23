import time
from datetime import datetime

from freezegun import freeze_time

from easyflake.sequence import ScaledClock


def test_current():
    with freeze_time("2020-01-01 00:00:00"):
        clock = ScaledClock(2, datetime(2020, 1, 1).timestamp())
        # Set the current time to 2020-01-01 00:01:01.12345
        # 1 minutes 1.12 seconds
        with freeze_time("2020-01-01 00:01:01.12345"):
            now = clock.current()
    assert now == 61_12, "Current time on the clock is not equal to 00:01:01.12"


def test_get_elapsed_timestamp():
    clock = ScaledClock(2, 1)
    with freeze_time("2023-01-01 00:00:00.123"):
        expected = int((time.time() - 1) * 100)
        now = clock.current()
    assert (
        clock.get_elapsed_time(now) == expected
    ), "Elapsed time from 1970-01-01 00:00:01 to 2023-01-01 00:00:00.123"


def test_bits_for_duration_hours():
    # Create a clock with scale 0 and epoch at the current time
    with freeze_time("2020-01-01 00:00:00"):
        clock = ScaledClock(0, epoch=time.time())

        # Calculate the expected number of bits required to represent 1 hour duration
        duration = 60**2
        expected = len(bin(duration)[2:])

        # Get the number of bits required to represent 1 hour duration on the clock,
        # and check that it is equal to the expected value
        result = clock.bits_for_duration(hours=1)
        assert (
            result == expected
        ), "Bits required for 1 hour duration is not equal to the expected value"


def test_bits_for_duration_days():
    # Create a clock with scale 1 and epoch at the current time
    with freeze_time("2020-01-01 00:00:00"):
        clock = ScaledClock(1, epoch=time.time())

        # Calculate the expected number of bits required to represent 1 day duration
        duration = 60**2 * 24
        expected = len(bin(duration * 10)[2:])

        # Get the number of bits required to represent 1 day duration on the clock,
        # and check that it is equal to the expected value
        result = clock.bits_for_duration(days=1)
        assert (
            result == expected
        ), "Bits required for 1 day duration is not equal to the expected value"


def test_bits_for_duration_years():
    # Create a clock with scale 1 and epoch at the current time
    with freeze_time("2020-01-01 00:00:00"):
        clock = ScaledClock(2, epoch=time.time())

        # Calculate the expected number of bits required to represent 1 year duration
        duration = 60**2 * 24 * 365
        expected = len(bin(duration * 100)[2:])

        # Get the number of bits required to represent 1 year duration on the clock,
        # and check that it is equal to the expected value
        result = clock.bits_for_duration(years=1)
        assert (
            result == expected
        ), "Bits required for 1 year duration is not equal to the expected value"
