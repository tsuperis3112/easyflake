import os
from datetime import datetime

import pytest

from easyflake.node.file import LIFESPAN, NodeIdPool

current = datetime(2023, 3, 4).timestamp()
expire = current + 1

existing_lines_10bits = [
    f"10:0:{expire}",
    f"10:1:{current}",
    f"10:2:{current}",
    f"10:3:{current}",
    "",
]

existing_lines_2bits = [
    f"2:0:{current}",
    f"2:1:{current}",
    f"2:2:{current}",
    f"2:3:{current}",
    "",
]


@pytest.fixture
def open_mock_10bits(mocker):
    filedata = os.linesep.join(existing_lines_10bits)
    return mocker.patch("builtins.open", new_callable=mocker.mock_open, read_data=filedata)


@pytest.fixture
def open_mock_2bits(mocker):
    filedata = os.linesep.join(existing_lines_2bits)
    return mocker.patch("builtins.open", new_callable=mocker.mock_open, read_data=filedata)


@pytest.fixture
def lock_file_mock(mocker):
    mocker.patch("easyflake.node.file.LockFile")


def test_NodeIdPool_listen(mocker, open_mock_10bits, lock_file_mock):
    mocker.patch("time.time", return_value=current)

    pool = NodeIdPool("file", 10)

    data_iter = pool.listen()
    assert next(data_iter) == 4

    written_lines = [*existing_lines_10bits[:-1], f"10:4:{current+LIFESPAN}"]
    written_data = os.linesep.join(written_lines)

    handler = open_mock_10bits()
    handler.write.assert_called_once_with(written_data)


def test_NodeIdPool_listen_expire_and_update(mocker, open_mock_10bits, lock_file_mock):
    mocker.patch("time.time", return_value=expire)

    pool = NodeIdPool("file", 10)

    data_iter = pool.listen()
    assert next(data_iter) == 1

    written_lines = [*existing_lines_10bits[:1], f"10:1:{expire+LIFESPAN}"]
    written_data = os.linesep.join(written_lines)

    handler = open_mock_10bits()
    handler.write.assert_called_once_with(written_data)


def test_NodeIdPool_listen_depleted(mocker, open_mock_2bits, lock_file_mock):
    err = EOFError
    mocker.patch("time.time", return_value=current)
    mocker.patch("time.sleep", side_effect=[None, EOFError])

    pool = NodeIdPool("file", 2)

    data_iter = pool.listen()
    with pytest.raises(err):
        next(data_iter)
