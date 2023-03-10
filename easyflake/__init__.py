from importlib import metadata

from easyflake.clock import TimeScale
from easyflake.easyflake import EasyFlake

__all__ = [
    "__version__",
    "EasyFlake",
    "TimeScale",
]

__version__ = metadata.metadata(__package__)["version"]
