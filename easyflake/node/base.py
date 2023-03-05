import abc
import multiprocessing
import random
from multiprocessing.sharedctypes import Synchronized
from typing import TYPE_CHECKING, Iterator

TIMEOUT = 3
INVALID_VALUE = -255


class NodeIdPool(abc.ABC):
    def __init__(self, endpoint: str, bits: int, *, timeout: int = TIMEOUT):
        self.bits = bits
        self.endpoint = endpoint
        self.timeout = timeout

        self._lock = multiprocessing.Lock()

        self._running_event = multiprocessing.Event()
        self._value_event = multiprocessing.Event()

        if TYPE_CHECKING:
            self._shared_node_id: Synchronized[int]
        else:
            self._shared_node_id = multiprocessing.Value("q", INVALID_VALUE)

    @property
    def refresh_rate(self):
        return self.timeout / 2 * random.random()

    def __del__(self):
        self.stop()

    @abc.abstractmethod
    def listen(self) -> Iterator[int]:
        """
        Listen for allocated node ID.
        Set status and node_id.
        """

    def _listen_forever(self):
        try:
            for seq in self.listen():
                with self._lock:
                    if not self._running_event.is_set():
                        return
                    self._node_id = seq
                    self._value_event.set()
        except Exception:
            self.fail()
        finally:
            self.stop()

    def start(self):
        with self._lock:
            if self._running_event.is_set():
                return
            self._running_event.set()

            proc = multiprocessing.Process(target=self._listen_forever, daemon=True)
            proc.start()

    def fail(self):
        with self._lock:
            self._node_id = INVALID_VALUE
            self._value_event.set()
            self._running_event.clear()

    def stop(self):
        with self._lock:
            self._value_event.clear()
            self._running_event.clear()

    def get(self) -> int:
        self.start()
        if self._value_event.wait(timeout=self.timeout):
            if (node_id := self._node_id) == INVALID_VALUE:
                raise ConnectionError("failed to listening server")
            return node_id
        raise TimeoutError("cannot get sequence value from server")

    @property
    def _node_id(self) -> int:
        return self._shared_node_id.value

    @_node_id.setter
    def _node_id(self, node_id: int):
        self._shared_node_id.value = node_id
