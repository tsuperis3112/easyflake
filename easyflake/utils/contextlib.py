from contextlib import ExitStack
from typing import ContextManager, Optional

__all__ = [
    "ContextStackManager",
]


class ContextStackManager:
    """

    >>> from unittest.mock import MagicMock
    >>> ctx = MagicMock()
    >>> stacked = ContextStackManager(None, ctx)
    >>> with stacked:
    ...     pass
    >>> ctx.__enter__.assert_called_once()
    >>> ctx.__exit__.assert_called_once()
    """

    def __init__(self, *locks: Optional[ContextManager]):
        self._ctx = [lck for lck in locks if lck is not None]

    def add(self, ctx: ContextManager):
        self._ctx.append(ctx)

    def __enter__(self):
        self.stack = ExitStack()
        try:
            for ctx in self._ctx:
                self.stack.enter_context(ctx)
        except Exception:
            self.stack.close()
            raise
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return self.stack.__exit__(exc_type, exc_value, traceback)
