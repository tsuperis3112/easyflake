from datetime import timedelta

import pytest

from easyflake import EasyFlake, TimeScale
from easyflake.node.base import NodeIdPool
from easyflake.sequence import TimeSequence


def test_get_id(mocker):
    timestamp = 123
    node_id = 456
    sequence = TimeSequence(timestamp=timestamp, value=789)

    ef = EasyFlake(node_id=node_id, node_id_bits=10, sequence_bits=9)
    mocker.patch(
        "easyflake.sequence.TimeSequenceProvider.next",
        return_value=sequence,
    )
    expected_id = timestamp << 19 | node_id << 9 | sequence.value
    actual_id = ef.get_id()
    msg = f"Generated ID {actual_id} is not equal to expected ID {expected_id}."
    assert actual_id == expected_id, msg


def test_get_id_with_node_id_provider(mocker):
    timestamp = 123
    node_id = 456
    sequence = TimeSequence(timestamp=timestamp, value=789)

    pool = mocker.patch("easyflake.node.base.NodeIdPool", spec=NodeIdPool)
    pool.get.return_value = node_id

    ef = EasyFlake(node_id=pool, node_id_bits=10, sequence_bits=9)

    mocker.patch(
        "easyflake.sequence.TimeSequenceProvider.next",
        return_value=sequence,
    )
    expected_id = timestamp << 19 | node_id << 9 | sequence.value
    actual_id = ef.get_id()
    msg = f"Generated ID {actual_id} is not equal to expected ID {expected_id}."
    assert actual_id == expected_id, msg


def test_instance_critical_lifetime(mocker):
    common_args = {
        "node_id": 0,
        "node_id_bits": 10,
        "sequence_bits": 10,
        "time_scale": TimeScale.SECOND,
    }

    # not dangerous lifetime
    mocker.patch(
        "easyflake.sequence.TimeSequenceProvider.get_required_bits",
        return_value=43,
    )
    EasyFlake(**common_args)

    mocker.patch(
        "easyflake.sequence.TimeSequenceProvider.get_required_bits",
        return_value=44,
    )
    # The ValueError should be raised for dangerous lifetime.
    with pytest.raises(ValueError):
        EasyFlake(**common_args)


def test_instance_dangerous_lifetime(mocker):
    common_args = {
        "node_id": 0,
        "node_id_bits": 10,
        "sequence_bits": 10,
        "time_scale": TimeScale.SECOND,
    }

    mocker.patch(
        "easyflake.easyflake.TimeSequenceProvider.get_required_bits",
        side_effect=lambda d: 43 if d <= timedelta(days=365) else 44,
    )
    # Assert that a warning is logged for dangerous lifetime
    warning_mock = mocker.patch("easyflake.easyflake.warning")

    EasyFlake(**common_args)
    warning_mock.assert_called_once()


def test_invalid_node_id():
    with pytest.raises(ValueError) as exc_info:
        EasyFlake(node_id=1024, node_id_bits=10)

    msg = "The error message should indicate that the node_id is invalid."
    assert "node_id" in str(exc_info), msg
    assert "<=1023" in str(exc_info), "The error reason is not valid."
