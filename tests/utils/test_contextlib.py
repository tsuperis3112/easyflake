from unittest.mock import MagicMock

import pytest

from easyflake.utils import contextlib


def test_stacked():
    ctx = MagicMock()
    stacked = contextlib.ContextStackManager(None, ctx)

    with stacked:
        pass

    ctx.__enter__.assert_called_once()
    ctx.__exit__.assert_called_once()


def test_add():
    ctx1 = MagicMock()
    ctx2 = MagicMock()

    stacked = contextlib.ContextStackManager(ctx1)
    stacked.add(ctx2)

    with stacked:
        pass

    ctx1.__enter__.assert_called_once()
    ctx1.__exit__.assert_called_once()

    ctx2.__enter__.assert_called_once()
    ctx2.__exit__.assert_called_once()


def test_with_error():
    ctx1 = MagicMock()
    ctx2 = MagicMock()
    ctx2.__enter__.side_effect = ValueError

    stacked = contextlib.ContextStackManager(ctx1, ctx2)

    with pytest.raises(ValueError):
        with stacked:
            pass

    ctx1.__enter__.assert_called_once()
    ctx1.__exit__.assert_called_once()

    ctx2.__enter__.assert_called_once()
    ctx2.__exit__.assert_not_called()
