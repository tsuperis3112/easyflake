import signal
import threading
import time
from enum import IntEnum
from multiprocessing import Value
from multiprocessing.sharedctypes import Synchronized
from typing import TYPE_CHECKING

import grpc

from easyflake.grpc.sequence_pb2 import SequenceReply, SequenceRequest
from easyflake.grpc.sequence_pb2_grpc import SequenceStub
from easyflake.log import logger


class _ListenStatus(IntEnum):
    STOPPED = 0
    RUNNING = 1
    EXHAUSTED = 2


RETRY = 5
INACTIVE_VALUE = -1


class Client:
    def __init__(self, endpoint: str, node_id_bits: int):
        channel = grpc.insecure_channel(endpoint)
        self._conn = SequenceStub(channel)
        self._lock = threading.Lock()

        self._status = Value("i", _ListenStatus.STOPPED)

        if TYPE_CHECKING:
            self._sequence: Synchronized[int]
        else:
            self._sequence = Value("q", INACTIVE_VALUE)
        self._node_id_bits = node_id_bits

        self._listen()

    def get_sequence(self):
        while True:
            if self._status.value != _ListenStatus.RUNNING:
                raise ConnectionAbortedError()
            if self._sequence.value >= 0:
                return self._sequence.value
            time.sleep(1)

    def _stop(self, *args, **kwargs):
        self._status.value = _ListenStatus.STOPPED

    def _listen(self):
        if self._status.value == _ListenStatus.RUNNING:
            return

        logger.debug("start listen sequence.")

        self._status.value = _ListenStatus.RUNNING
        observer = threading.Thread(target=self._throw_request, daemon=True)
        observer.start()

        signal.signal(signal.SIGINT | signal.SIGKILL | signal.SIGTERM, self._stop)

    def _throw_request(self):
        """
        when waiting for new messages
        """
        request = SequenceRequest(bits=self._node_id_bits)
        reply: SequenceReply

        for i in range(RETRY):
            try:
                for reply in self._conn.LiveStream(request):
                    if self._status.value != _ListenStatus.RUNNING:
                        logger.debug("gRPC connection is closed.")
                        break
                    self._sequence.value = reply.sequence
            except grpc.RpcError as e:
                if e.code() != grpc.StatusCode.OUT_OF_RANGE:
                    self._status.value = _ListenStatus.STOPPED
                    logger.exception(e)
                    break
                time.sleep(1 << i)
        else:
            self._status.value = _ListenStatus.EXHAUSTED

        self._sequence.value = INACTIVE_VALUE
