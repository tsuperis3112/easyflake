from easyflake.utils.singleton import Singleton


class DummySingleton(Singleton):
    def __init__(self, arg1, *args, argn=None, **kwargs):
        pass


def test_singleton_obj():
    class A:
        pass

    s1 = DummySingleton(A())
    s2 = DummySingleton(A())

    assert s1 == s2


def test_singleton_str():
    s1 = DummySingleton(arg1="str")
    s2 = DummySingleton("str")
    s3 = DummySingleton("str2")

    assert s1 == s2
    assert s2 != s3


def test_singleton_int():
    s1 = DummySingleton(arg1=1)
    s2 = DummySingleton(1)
    s3 = DummySingleton(2)

    assert s1 == s2
    assert s2 != s3


def test_singleton_bool():
    s1 = DummySingleton(arg1=True)
    s2 = DummySingleton(True)
    s3 = DummySingleton(False)

    assert s1 == s2
    assert s2 != s3


def test_singleton_tuple():
    s1 = DummySingleton(arg1=(1, 2, 3))
    s2 = DummySingleton((1, 2, 3))
    s3 = DummySingleton((1, 2, 3, 4))

    assert s1 == s2
    assert s2 != s3


def test_singleton_list():
    s1 = DummySingleton(arg1=[1, 2, 3])
    s2 = DummySingleton([1, 2, 3])
    s3 = DummySingleton([1, 2, 3, 4])

    assert s1 == s2
    assert s2 != s3


def test_singleton_set():
    s1 = DummySingleton(arg1={1, 2, 3})
    s2 = DummySingleton({1, 2, 3})
    s3 = DummySingleton({1, 2, 3, 4})

    assert s1 == s2
    assert s2 != s3


def test_singleton_dict():
    class A:
        pass

    s1 = DummySingleton(arg1={"a": A()})
    s2 = DummySingleton({"a": A()})
    s3 = DummySingleton({"a": A(), "b": A()})

    assert s1 == s2
    assert s2 != s3


def test_singleton_change_arg_sort():
    s1 = DummySingleton(argn="N", arg1=1, arg2=2)
    s2 = DummySingleton(1, arg2=2, argn="N")

    assert s1 == s2
