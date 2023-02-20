from pathlib import Path

import toml

from .clock import TimeScale
from .easyflake import EasyFlake

__all__ = [
    "__version__",
    "EasyFlake",
    "TimeScale",
]


def _get_version():
    path = Path(__file__).resolve().parents[2] / "pyproject.toml"
    pyproject = toml.loads(open(str(path)).read())
    return pyproject["tool"]["poetry"]["version"]


__version__ = _get_version()
