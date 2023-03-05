from datetime import datetime, timedelta

import pytest

from easyflake.exceptions import SequenceOverflowError
from easyflake.sequence import SimpleSequencePool, TimeSequence, TimeSequenceProvider


def test_TimeSequenceProvider_get_required_bits(mocker):
    provider = TimeSequenceProvider(bits=2, epoch=datetime(2023, 2, 8).timestamp(), time_scale=2)

    # 10.23
    mocker.patch("time.time", return_value=datetime(2023, 2, 8, 0, 0, 1, 231000).timestamp())
    actual = provider.get_required_bits(timedelta(seconds=9))
    expected = 10  # 1023
    assert actual == expected, "1023 (10.23sec) requires 10 bits."

    # 10.24
    mocker.patch("time.time", return_value=datetime(2023, 2, 8, 0, 0, 1, 240000).timestamp())
    actual = provider.get_required_bits(timedelta(seconds=10))
    expected = 11  # 1024
    assert actual == expected, "1024 (10.24sec) requires 11 bits."


def test_TimeSequenceProvider_next(mocker):
    first_tick = datetime(2023, 2, 8, 12, 24, 0).timestamp()
    second_tick = datetime(2023, 2, 8, 12, 24, 12, 345000).timestamp()
    third_tick = datetime(2023, 2, 8, 12, 24, 12, 346000).timestamp()
    fourth_tick = datetime(2023, 2, 8, 12, 24, 12, 350000).timestamp()

    provider = TimeSequenceProvider(bits=2, epoch=first_tick, time_scale=2)

    # 12.345 sec after
    mocker.patch("time.time", return_value=second_tick)
    sleep_mock = mocker.patch("time.sleep", side_effect=[None, StopIteration])

    # Generate two IDs and check if they are equal to the expected IDs
    for i in range(4):  # loop for 2 bits
        msg = f"ID generated ({i} times) is not equal to expected"
        expected = TimeSequence(timestamp=1234, value=i)
        assert provider.next() == expected, msg

    sleep_mock.assert_not_called()

    # Verify that a sleep is called when the sequence reaches the maximum value
    mocker.patch("time.time", return_value=third_tick)
    with pytest.raises(StopIteration):
        provider.next()
    sleep_mock.assert_called()

    # Generate an ID after 1 unit time
    mocker.patch("time.time", return_value=fourth_tick)
    sleep_mock = mocker.patch("time.sleep", side_effect=StopIteration)

    msg = "ID generated after 1 unit time is not equal to expected ID"
    expected = TimeSequence(timestamp=1235, value=0)
    assert provider.next() == expected, msg

    sleep_mock.assert_not_called()


def test_SimpleSequencePool_pop():
    bits = 2
    expected_set = {0, 1, 2, 3}

    pool = SimpleSequencePool()
    values = set()

    for _ in range(len(expected_set)):
        values.add(pool.pop(bits))

    with pytest.raises(SequenceOverflowError):
        pool.pop(bits)

    assert values == expected_set


def test_SimpleSequencePool_push():
    bits = 2
    max_value = (1 << bits) - 1

    pool = SimpleSequencePool()
    pool.pop(bits)

    pool.push(bits, 0)
    with pytest.raises(ValueError):
        pool.push(bits, -1)

    pool.push(bits, max_value)
    with pytest.raises(ValueError):
        pool.push(bits, max_value + 1)


def test_SimpleSequencePool_rm():
    bits = 2

    remove_value = 2
    expected_set = {0, 1, 3}

    pool = SimpleSequencePool()
    pool.rm(bits, remove_value)

    values = {pool.pop(bits) for _ in range(len(expected_set))}

    assert values == expected_set
