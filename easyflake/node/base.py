import abc


class BaseNodeFactory(abc.ABC):
    @abc.abstractmethod
    def get_node_id(self, bits: int) -> int:
        ...
