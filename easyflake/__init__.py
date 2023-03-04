from importlib import metadata

from .clock import Scale
from .easyflake import EasyFlake

__all__ = [
    "__version__",
    "EasyFlake",
    "Scale",
]

__version__ = metadata.metadata(__package__)["version"]
