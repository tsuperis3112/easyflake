from importlib import metadata

from .clock import TimeScale
from .easyflake import EasyFlake
from .node import *  # noqa

__all__ = [
    "__version__",
    "EasyFlake",
    "TimeScale",
]

__version__ = metadata.metadata(__package__)["version"]
