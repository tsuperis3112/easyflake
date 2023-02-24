import abc


class BaseNodeFactory(abc.ABC):
    @abc.abstractmethod
    def get_id(self, bits: int) -> int:
        ...
