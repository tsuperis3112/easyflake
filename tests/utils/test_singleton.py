import sys

import pytest

from easyflake.utils.singleton import SingletonMeta


@pytest.fixture
def singleton_class():
    class Singleton(metaclass=SingletonMeta):
        def __init__(self, arg1, *args, argn=None, **kwargs):
            pass

    return Singleton


@pytest.mark.skipif(sys.version_info >= (3, 9), reason="only test for python3.8")
def test_singleton(singleton_class):
    class A:
        pass

    s1 = singleton_class(A(), argn=1, arg2={"a": "A", "b": 2})
    s2 = singleton_class(A(), argn=1, arg2={"a": "A", "b": 2})
    s3 = singleton_class(A(), argn=2, arg2={"a": "A", "b": 2})

    assert s1 == s2
    assert s2 != s3


@pytest.mark.skipif(
    sys.version_info < (3, 9),
    reason="The inspect module does not provide a complete list of arguments",
)
def test_singleton_obj(singleton_class):
    class A:
        pass

    a = A()
    s1 = singleton_class(a)
    s2 = singleton_class(arg1=a)

    assert s1 == s2


@pytest.mark.skipif(
    sys.version_info < (3, 9),
    reason="The inspect module in does not provide a complete list of arguments",
)
def test_singleton_str(singleton_class):
    s1 = singleton_class(arg1="str")
    s2 = singleton_class("str")
    s3 = singleton_class("str2")

    assert s1 == s2
    assert s2 != s3


@pytest.mark.skipif(
    sys.version_info < (3, 9),
    reason="The inspect module in does not provide a complete list of arguments",
)
def test_singleton_int(singleton_class):
    s1 = singleton_class(arg1=1)
    s2 = singleton_class(1)
    s3 = singleton_class(2)

    assert s1 == s2
    assert s2 != s3


@pytest.mark.skipif(
    sys.version_info < (3, 9),
    reason="The inspect module in does not provide a complete list of arguments",
)
def test_singleton_bool(singleton_class):
    s1 = singleton_class(arg1=True)
    s2 = singleton_class(True)
    s3 = singleton_class(False)

    assert s1 == s2
    assert s2 != s3


@pytest.mark.skipif(
    sys.version_info < (3, 9),
    reason="The inspect module in does not provide a complete list of arguments",
)
def test_singleton_tuple(singleton_class):
    s1 = singleton_class(arg1=(1, 2, 3))
    s2 = singleton_class((1, 2, 3))
    s3 = singleton_class((1, 2, 3, 4))

    assert s1 == s2
    assert s2 != s3


@pytest.mark.skipif(
    sys.version_info < (3, 9),
    reason="The inspect module in does not provide a complete list of arguments",
)
def test_singleton_list(singleton_class):
    s1 = singleton_class(arg1=[1, 2, 3])
    s2 = singleton_class([1, 2, 3])
    s3 = singleton_class([1, 2, 3, 4])

    assert s1 == s2
    assert s2 != s3


@pytest.mark.skipif(
    sys.version_info < (3, 9),
    reason="The inspect module in does not provide a complete list of arguments",
)
def test_singleton_set(singleton_class):
    s1 = singleton_class(arg1={1, 2, 3})
    s2 = singleton_class({1, 2, 3})
    s3 = singleton_class({1, 2, 3, 4})

    assert s1 == s2
    assert s2 != s3


@pytest.mark.skipif(
    sys.version_info < (3, 9),
    reason="The inspect module in does not provide a complete list of arguments",
)
def test_singleton_dict(singleton_class):
    class A:
        pass

    s1 = singleton_class(arg1={"a": A()})
    s2 = singleton_class({"a": A()})
    s3 = singleton_class({"a": A(), "b": A()})

    assert s1 == s2
    assert s2 != s3


@pytest.mark.skipif(
    sys.version_info < (3, 9),
    reason="The inspect module in does not provide a complete list of arguments",
)
def test_singleton_change_arg_sort(singleton_class):
    s1 = singleton_class(argn="N", arg1=1, arg2=2)
    s2 = singleton_class(1, arg2=2, argn="N")

    assert s1 == s2
