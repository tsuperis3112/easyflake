from logging import getLogger

logger = getLogger("easyflake")
logger_grpc = getLogger("easyflake.grpc")


def _format(prefix, message):
    return f"{prefix}: {message}"


def warn(message, *args):
    message = _format("WARN", message)
    logger.warn(message, *args)
