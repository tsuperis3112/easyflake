from logging import getLogger

logger = getLogger("easyflake")


def _format(prefix, message):
    return f"{prefix}: {message}"


def warn(message, *args):
    message = _format("WARN", message)
    logger.warn(message, *args)
