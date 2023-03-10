import abc
import inspect
import threading


class SingletonMeta(type):
    """
    The Singleton class can be implemented in different ways in Python. Some
    possible methods include: base class, decorator, metaclass. We will use the
    metaclass because it is best suited for this purpose.
    """

    def __new__(cls, cls_name, cls_bases, cls_dict):
        cls_dict.update({"__singleton_lock__": threading.Lock(), "__singleton_instances__": {}})
        return super().__new__(cls, cls_name, cls_bases, cls_dict)

    def __call__(self, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        cls_id = id(self)

        signature = inspect.signature(self.__init__)
        bound_args = signature.bind(cls_id, *args, **kwargs)
        args_hash = _recursive_hash(bound_args.arguments.items())

        with self.__singleton_lock__:
            instances = self.__singleton_instances__
            if args_hash not in instances:
                instances[args_hash] = super().__call__(*args, **kwargs)

        return instances[args_hash]


class SingletonABCMeta(abc.ABCMeta, SingletonMeta):
    ...


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
