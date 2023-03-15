import abc
import multiprocessing
import random
import time
from multiprocessing.sharedctypes import Synchronized
from typing import TYPE_CHECKING, Iterator, Optional

from easyflake import logging
from easyflake.utils.singleton import SingletonABCMeta

TIMEOUT = 5
INVALID_VALUE = -255


class NodeIdPool(metaclass=SingletonABCMeta):
    def __init__(self, endpoint: str, bits: int, *, timeout: int = TIMEOUT):
        """
        Base class for each NodeIdPool.
        This class provides a `get` method to allocated node ID.

        Subclasses should implement the `listen` method.
        """
        self.bits = bits
        self.endpoint = endpoint
        self.timeout = timeout

        # Shared objects
        self._subprocess: Optional[multiprocessing.Process] = None
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
        try:
            self.stop()
        except OSError:  # pragma: nocover
            pass

    @abc.abstractmethod
    def listen(self) -> Iterator[Optional[int]]:
        """Listen for allocated node ID."""

    def _start_listening(self):
        self._subprocess = None
        try:
            for seq in self.listen():
                with self._lock:
                    if not self._running_event.is_set():
                        return
                    if seq is not None:
                        self._node_id = seq
                        self._value_event.set()
                time.sleep(self.refresh_rate)
            else:
                self.stop()

        except KeyboardInterrupt:
            self.stop()

        except Exception as e:
            logging.exception(e)
            self.fail()

    def _stop_listening(self):
        self._running_event.clear()
        try:
            if self._subprocess is not None:
                self._subprocess.kill()
                self._subprocess = None
        except Exception:
            pass

    def start(self):
        with self._lock:
            if self._running_event.is_set():
                return
            self._running_event.set()

            self._subprocess = multiprocessing.Process(target=self._start_listening, daemon=True)
            self._subprocess.start()

    def fail(self):
        with self._lock:
            self._node_id = INVALID_VALUE
            self._value_event.set()
            self._stop_listening()

    def stop(self):
        with self._lock:
            self._value_event.clear()
            self._stop_listening()

    def get(self) -> int:
        self.start()

        if not self._value_event.wait(timeout=self.timeout):
            raise TimeoutError("cannot get sequence value from server")

        node_id = self._node_id
        if node_id == INVALID_VALUE:
            raise ConnectionError("failed to listening server")
        return node_id

    @property
    def _node_id(self) -> int:
        return self._shared_node_id.value

    @_node_id.setter
    def _node_id(self, node_id: int):
        self._shared_node_id.value = node_id
