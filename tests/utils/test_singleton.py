import sys

import pytest

from easyflake.utils.singleton import Singleton


class DummySingleton(Singleton):
    def __init__(self, arg1, *args, argn=None, **kwargs):
        pass


@pytest.mark.skipif(sys.version_info >= (3, 9), reason="only test for python3.8")
def test_singleton():
    class A:
        pass

    s1 = DummySingleton(A(), argn=1, arg2={"a": "A", "b": 2})
    s2 = DummySingleton(A(), argn=1, arg2={"a": "A", "b": 2})
    s3 = DummySingleton(A(), argn=2, arg2={"a": "A", "b": 2})

    assert s1 == s2
    assert s2 != s3


@pytest.mark.skipif(
    sys.version_info < (3, 9),
    reason="The inspect module does not provide a complete list of arguments",
)
def test_singleton_obj():
    class A:
        pass

    s1 = DummySingleton(A())
    s2 = DummySingleton(A())

    assert s1 == s2


@pytest.mark.skipif(
    sys.version_info < (3, 9),
    reason="The inspect module in does not provide a complete list of arguments",
)
def test_singleton_str():
    s1 = DummySingleton(arg1="str")
    s2 = DummySingleton("str")
    s3 = DummySingleton("str2")

    assert s1 == s2
    assert s2 != s3


@pytest.mark.skipif(
    sys.version_info < (3, 9),
    reason="The inspect module in does not provide a complete list of arguments",
)
def test_singleton_int():
    s1 = DummySingleton(arg1=1)
    s2 = DummySingleton(1)
    s3 = DummySingleton(2)

    assert s1 == s2
    assert s2 != s3


@pytest.mark.skipif(
    sys.version_info < (3, 9),
    reason="The inspect module in does not provide a complete list of arguments",
)
def test_singleton_bool():
    s1 = DummySingleton(arg1=True)
    s2 = DummySingleton(True)
    s3 = DummySingleton(False)

    assert s1 == s2
    assert s2 != s3


@pytest.mark.skipif(
    sys.version_info < (3, 9),
    reason="The inspect module in does not provide a complete list of arguments",
)
def test_singleton_tuple():
    s1 = DummySingleton(arg1=(1, 2, 3))
    s2 = DummySingleton((1, 2, 3))
    s3 = DummySingleton((1, 2, 3, 4))

    assert s1 == s2
    assert s2 != s3


@pytest.mark.skipif(
    sys.version_info < (3, 9),
    reason="The inspect module in does not provide a complete list of arguments",
)
def test_singleton_list():
    s1 = DummySingleton(arg1=[1, 2, 3])
    s2 = DummySingleton([1, 2, 3])
    s3 = DummySingleton([1, 2, 3, 4])

    assert s1 == s2
    assert s2 != s3


@pytest.mark.skipif(
    sys.version_info < (3, 9),
    reason="The inspect module in does not provide a complete list of arguments",
)
def test_singleton_set():
    s1 = DummySingleton(arg1={1, 2, 3})
    s2 = DummySingleton({1, 2, 3})
    s3 = DummySingleton({1, 2, 3, 4})

    assert s1 == s2
    assert s2 != s3


@pytest.mark.skipif(
    sys.version_info < (3, 9),
    reason="The inspect module in does not provide a complete list of arguments",
)
def test_singleton_dict():
    class A:
        pass

    s1 = DummySingleton(arg1={"a": A()})
    s2 = DummySingleton({"a": A()})
    s3 = DummySingleton({"a": A(), "b": A()})

    assert s1 == s2
    assert s2 != s3


@pytest.mark.skipif(
    sys.version_info < (3, 9),
    reason="The inspect module in does not provide a complete list of arguments",
)
def test_singleton_change_arg_sort():
    s1 = DummySingleton(argn="N", arg1=1, arg2=2)
    s2 = DummySingleton(1, arg2=2, argn="N")

    assert s1 == s2
