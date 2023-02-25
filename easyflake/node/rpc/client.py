import threading
import time
from enum import IntEnum
from multiprocessing import Lock, Value
from multiprocessing.sharedctypes import Synchronized
from typing import TYPE_CHECKING

import grpc
from grpc import StatusCode

from easyflake.grpc.protobuf.sequence_pb2 import SequenceReply, SequenceRequest
from easyflake.grpc.protobuf.sequence_pb2_grpc import SequenceStub


class ListenStatus(IntEnum):
    STOPPED = 0
    RUNNING = 1
    OVERFLOW = 2
    ERROR = 4


RETRY = 5
INACTIVE_VALUE = -1


class RpcClient:
    def __init__(self, endpoint: str, node_id_bits: int, *, retry: int = RETRY):
        self._node_id_bits = node_id_bits
        self._endpoint = endpoint
        self._retry = retry

        self._lock = Lock()
        if TYPE_CHECKING:
            self._shared_connection_id: Synchronized[int]
            self._shared_status: Synchronized[int]
        else:
            self._shared_connection_id = Value("q", INACTIVE_VALUE)
            self._shared_status = Value("i", ListenStatus.STOPPED)

        self.listen()

    def _connect(self):
        self._channel = grpc.insecure_channel(self._endpoint)
        self._conn = SequenceStub(self._channel)

    def stop(self):
        with self._shared_status.get_lock():
            if self._shared_status.value == ListenStatus.RUNNING:
                self._shared_status.value = ListenStatus.STOPPED
                self._channel.close()

    def _sleep_n(self, n: int):
        if n < self._retry - 1:
            time.sleep((1 << n) / 2)

    def get_connection_id(self):
        aborted = False

        for i in range(self._retry):
            if self._shared_status.value != ListenStatus.RUNNING:
                # If the server connection has been aborted
                if aborted:
                    break
                else:
                    self.listen()
                    aborted = True

            if self._shared_connection_id.value >= 0:
                return self._shared_connection_id.value

            self._sleep_n(i)

        if aborted:
            raise ConnectionAbortedError("connection to gRPC server is aborted")
        else:
            raise TimeoutError("cannot get sequence value from server")

    def listen(self):
        with self._shared_status.get_lock():
            if self._shared_status.value == ListenStatus.RUNNING:
                return
            self._shared_status.value = ListenStatus.RUNNING

        observer = threading.Thread(target=self._listen, daemon=True)
        observer.start()

    def _listen(self):
        """listen allocated connection ID"""
        # create connection to the gRPC server and and connection ID
        with self._lock:
            self._connect()

            request = SequenceRequest(bits=self._node_id_bits)
            reply: SequenceReply

            # Attempt to retrieve connection ID from the server
            for i in range(RETRY):
                try:
                    for reply in self._conn.LiveStream(request):
                        self._shared_connection_id.value = reply.sequence

                except Exception as e:
                    if isinstance(e, grpc.Call):
                        code = e.code()
                        if code in (StatusCode.UNAVAILABLE, StatusCode.CANCELLED):
                            # stop listening if the connection is cancelled
                            self._shared_status.value = ListenStatus.STOPPED
                            break
                        elif code == StatusCode.OUT_OF_RANGE:
                            # retry after a sleep when a sequence overflow occurs
                            self._sleep_n(i)
                            continue

                    self._shared_status.value = ListenStatus.ERROR
                    raise
            else:
                self._shared_status.value = ListenStatus.OVERFLOW

            self._shared_connection_id.value = INACTIVE_VALUE
