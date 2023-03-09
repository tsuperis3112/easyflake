import inspect
import threading
from typing import Any, Dict


class Singleton(object):
    _instances: Dict[int, Any] = {}
    _thread_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        signature = inspect.signature(cls)
        bound_args = signature.bind(*args, **kwargs)
        arg_hash = _recursive_hash(bound_args.arguments.items())

        with cls._thread_lock:
            if arg_hash not in cls._instances:
                cls._instances[arg_hash] = super().__new__(cls)

        return cls._instances[arg_hash]


def _recursive_hash(obj):
    """
    >>> assert _recursive_hash("a") == _recursive_hash("a")
    >>> assert _recursive_hash("a") != _recursive_hash("b")
    >>> assert _recursive_hash(1) == _recursive_hash(1)
    >>> assert _recursive_hash(1) != _recursive_hash(2)
    >>> assert _recursive_hash({"a": 1}) == _recursive_hash({"a": 1})
    >>> assert _recursive_hash({"a": 1}) != _recursive_hash({"a": 2})
    >>> assert _recursive_hash([1, 2, 3]) == _recursive_hash([1, 2, 3])
    >>> assert _recursive_hash([1, 2, 3]) != _recursive_hash([1, 2, 4])
    >>> assert _recursive_hash({1, 2, 3}) == _recursive_hash({1, 2, 3})
    >>> assert _recursive_hash({1, 2, 3}) != _recursive_hash({1, 2, 4})
    >>> class A:
    ...     def __init__(self): ...
    ...
    >>> a1 = a2 = A()
    >>> a3 = A()
    >>> assert _recursive_hash(a1) == _recursive_hash(a2)
    >>> assert _recursive_hash(a2) != _recursive_hash(a3)
    """
    if isinstance(obj, (int, str, float, bool, tuple)):
        return hash(obj)

    if isinstance(obj, dict):
        hash_list = [_recursive_hash(k) ^ _recursive_hash(v) for k, v in obj.items()]
        return sum(hash_list)

    if isinstance(obj, list):
        hash_list = tuple(_recursive_hash(elem) for elem in obj)
        return hash(hash_list)

    if isinstance(obj, set):
        hash_list = tuple(_recursive_hash(elem) for elem in obj)
        return hash(hash_list)

    if obj_hash := getattr(obj, "__hash__", None):
        return obj_hash()

    return hash(str(obj))
