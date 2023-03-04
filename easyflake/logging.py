import logging
import os
import traceback
from typing import Optional

import click

from easyflake import config

logger = logging.getLogger("easyflake")


def _console(loglevel: int, message: str, *args, color: Optional[str] = None):
    level_name = logging.getLevelName(loglevel)
    message = f"[%s] {message}" % (level_name, *args)
    if color and config.COLOR_MODE:
        message = click.style(message, fg=color)
    click.echo(message)


def debug(message: str, *args):
    if config.DAEMON_MODE:
        logger.debug(message, *args)
    elif config.DEBUG_MODE:
        _console(logging.DEBUG, message, *args)


def info(message: str, *args):
    if config.DAEMON_MODE:
        logger.info(message, *args)
    else:
        _console(logging.INFO, message, *args)


def success(message: str, *args):
    if config.DAEMON_MODE:
        logger.info(message, *args)
    else:
        _console(logging.INFO, message, *args, color="green")


def warning(message: str, *args):
    if config.DAEMON_MODE:
        logger.warning(message)
    else:
        _console(logging.WARNING, message, *args, color="yellow")


def error(message: str, *args):
    if config.DAEMON_MODE:
        logger.error(message)
    else:
        _console(logging.ERROR, message, *args, color="red")


def exception(e: Exception):
    if config.DAEMON_MODE:
        logger.exception(e)
    else:
        lines = traceback.format_exception(type(e), value=e, tb=e.__traceback__)
        error(os.linesep.join(lines))
