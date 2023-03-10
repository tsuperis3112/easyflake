import os
from datetime import datetime

import pytest

from easyflake.exceptions import SequenceOverflowError
from easyflake.node.file import LIFESPAN, LineStruct, NodeIdPool

current = datetime(2023, 3, 4).timestamp()
expire = current + 1

existing_lines_10bits = [
    f"10:0:{expire}",
    f"10:1:{current}",
    f"10:2:{current}",
    f"10:3:{current}",
    "",
]

expected_sequence = 4

existing_lines_2bits = [
    f"2:0:{current}",
    f"2:1:{current}",
    f"2:2:{current}",
    f"2:3:{current}",
    "",
]


def _create_open_mock(mocker, data: str):
    return mocker.patch("builtins.open", new_callable=mocker.mock_open, read_data=data)


@pytest.fixture
def open_mock_10bits(mocker):
    filedata = os.linesep.join(existing_lines_10bits)
    return _create_open_mock(mocker, filedata)


@pytest.fixture
def open_mock_2bits(mocker):
    filedata = os.linesep.join(existing_lines_2bits)
    return mocker.patch("builtins.open", new_callable=mocker.mock_open, read_data=filedata)


@pytest.fixture
def lock_file_mock(mocker):
    mocker.patch("easyflake.node.file.LockFile")


@pytest.fixture
def target_class():
    yield NodeIdPool
    NodeIdPool.__singleton_instances__ = {}


def test_NodeIdPool_listen(mocker, target_class, open_mock_10bits, lock_file_mock):
    bits = 10
    mocker.patch("time.time", return_value=current)

    pool = target_class("file", bits)

    data_iter = pool.listen()
    assert next(data_iter) == expected_sequence

    written_lines = [*existing_lines_10bits[:-1], f"{bits}:{expected_sequence}:{current+LIFESPAN}"]
    written_data = os.linesep.join(written_lines)

    handler = open_mock_10bits()
    handler.write.assert_called_once_with(written_data)


def test_NodeIdPool_listen_update(mocker, target_class, open_mock_10bits, lock_file_mock):
    bits = 10

    handler = open_mock_10bits()
    pool = target_class("file", bits).listen()

    # current
    mocker.patch("time.time", return_value=current)

    assert next(pool) == expected_sequence

    updated_written_lines = [
        *existing_lines_10bits[:-1],
        f"{bits}:{expected_sequence}:{current+LIFESPAN}",
    ]
    written_data = os.linesep.join(updated_written_lines)
    handler.write.assert_called_with(written_data)

    # update
    updated_open_mock = _create_open_mock(mocker, written_data)
    handler = updated_open_mock()
    mocker.patch("time.time", return_value=expire)
    mocker.patch("time.sleep")

    assert next(pool) == expected_sequence

    updated_written_lines = [
        *existing_lines_10bits[:1],
        f"{bits}:{expected_sequence}:{expire+LIFESPAN}",
    ]
    updated_written_data = os.linesep.join(updated_written_lines)
    handler.write.assert_called_with(updated_written_data)


def test_NodeIdPool_listen_depleted(mocker, target_class, open_mock_2bits, lock_file_mock):
    bits = 2
    mocker.patch(
        "easyflake.node.grpc.SimpleSequencePool.pop", side_effect=SequenceOverflowError(bits)
    )

    pool = target_class("file", bits)

    data_iter = pool.listen()
    assert next(data_iter) is None


def test_LineStruct_parse_valid():
    line = LineStruct.parse("1:10:100.0")
    assert line is not None
    assert line.bits == 1
    assert line.sequence == 10
    assert line.expire == 100.0


def test_LineStruct_parse_invalid():
    line = LineStruct.parse("1:10:100.a")
    assert line is None
