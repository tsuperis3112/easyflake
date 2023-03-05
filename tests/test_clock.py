from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest

from easyflake.clock import ClockScaler, Scale

base_datetime = datetime(1970, 1, 1, 0, 1, 1, 234567, tzinfo=timezone.utc)
diff_from_epoch = 61_23


@pytest.fixture
def time_mock(mocker):
    mocker.patch("time.time", return_value=base_datetime.timestamp())


def test_invalid_arguments():
    ClockScaler(2, Scale.SECOND)
    with pytest.raises(ValueError):
        ClockScaler(Scale.SECOND - 1, 0)

    ClockScaler(2, Scale.MICRO)
    with pytest.raises(ValueError):
        ClockScaler(Scale.MICRO + 1, 0)


def test_current(time_mock):
    clock = ClockScaler(2, 0)
    # Set the current time to 2020-01-01 00:01:01.12345
    # 1 minutes 1.12 seconds
    now = clock.current()
    assert now == diff_from_epoch, "Current time on the clock is not equal to 00:01:01.12"


def test_future(time_mock):
    # Create a clock with scale 0 and epoch at the current time
    clock = ClockScaler(2, 0)

    # Calculate the expected number of bits required to represent 1 hour duration
    delta = timedelta(hours=1, microseconds=123456)
    expected = 3600_12 + diff_from_epoch

    # Get the number of bits required to represent 1 hour duration on the clock,
    # and check that it is equal to the expected value
    result = clock.future(delta)
    assert (
        result == expected
    ), "Bits required for 1 hour duration is not equal to the expected value"


def test_sleep():
    with patch("time.sleep") as sleep_mock:
        clock = ClockScaler(Scale.MILLI, 0)
        clock.sleep(0, 3)
        sleep_mock.assert_called_once_with(0.003)
