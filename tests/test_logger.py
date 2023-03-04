import pytest
from pytest_mock import MockerFixture

from easyflake import logging


@pytest.fixture(autouse=True)
def logger_mock(mocker: MockerFixture):
    mocker.patch("easyflake.logging.logger")


@pytest.fixture
def daemon_mode(mocker):
    mocker.patch("easyflake.logging.config.DAEMON_MODE", True)


@pytest.fixture
def debug_mode(mocker):
    mocker.patch("easyflake.logging.config.DEBUG_MODE", True)


def test_debug(daemon_mode):
    logging.debug("message")
    logging.logger.debug.assert_called_once_with("message")


def test_info(daemon_mode):
    # with self.config_mock:
    logging.info("message")
    logging.logger.info.assert_called_once_with("message")


def test_success(daemon_mode):
    # with self.config_mock:
    logging.success("message")
    logging.logger.info.assert_called_once_with("message")


def test_warning(daemon_mode):
    # with self.config_mock:
    logging.warning("message")
    logging.logger.warning.assert_called_once_with("message")


def test_error(daemon_mode):
    # with self.config_mock:
    logging.error("message")
    logging.logger.error.assert_called_once_with("message")


def test_exception(daemon_mode):
    # with self.config_mock:
    err = RuntimeError("test")
    try:
        raise err
    except Exception as e:
        logging.exception(e)
    logging.logger.exception.assert_called_once_with(err)


def test_debug_stdio(debug_mode, capsys):
    logging.debug("message")
    captured = capsys.readouterr()
    assert "[DEBUG] message\n" == captured.out


def test_no_debug_stdio(capsys):
    logging.debug("message")
    captured = capsys.readouterr()
    assert "" == captured.out


def test_info_stdout(capsys):
    logging.info("message")
    captured = capsys.readouterr()
    assert "[INFO] message\n" == captured.out


def test_success_stdout(capsys):
    logging.success("message")
    captured = capsys.readouterr()
    assert "[INFO] message\n" == captured.out


def test_warning_stdout(capsys):
    logging.warning("message")
    captured = capsys.readouterr()
    assert "[WARNING] message\n" == captured.out


def test_error_stdout(capsys):
    logging.error("message")
    captured = capsys.readouterr()
    assert "[ERROR] message\n" == captured.out


def test_exception_stdout(capsys):
    try:
        raise RuntimeError("test", "???")
    except Exception as e:
        logging.exception(e)

    captured = capsys.readouterr()
    output = captured.out

    assert output.startswith("[ERROR] Traceback")
    assert 'raise RuntimeError("test", "???")' in output
