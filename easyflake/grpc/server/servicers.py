import random
import signal
import time
from collections import defaultdict
from threading import Lock
from typing import DefaultDict, Set

import grpc

from easyflake import logging
from easyflake.exceptions import SequenceOverflowError
from easyflake.grpc.protobuf import sequence_pb2, sequence_pb2_grpc


class SequenceServicer(sequence_pb2_grpc.SequenceServicer):
    def __init__(self):
        # bits: sequences
        self._sequences_by_bits: DefaultDict[int, Set[int]] = defaultdict(set)
        self._lock = Lock()

    def take_sequence(self, bits: int):
        with self._lock:
            sequence_set = self._sequences_by_bits[bits]
            for i in range(2**bits):
                if i not in sequence_set:
                    sequence_set.add(i)
                    return i
            else:
                raise SequenceOverflowError(bits)

    def cleanup_sequence(self, bits: int, sequence: int):
        with self._lock:
            sequence_set = self._sequences_by_bits[bits]
            if sequence in sequence_set:
                sequence_set.remove(sequence)

    def LiveStream(
        self, request: sequence_pb2.SequenceRequest, context: grpc.ServicerContext
    ):
        logging.debug("connection established")

        try:
            sequence = self.take_sequence(request.bits)
        except SequenceOverflowError as e:
            context.abort(grpc.StatusCode.OUT_OF_RANGE, str(e))
            return

        # wait unless connection is closed
        while True:
            if not context.is_active():
                logging.debug("connection %s is closed", sequence)
                self.cleanup_sequence(request.bits, sequence)
                break

            yield sequence_pb2.SequenceReply(sequence=sequence)
            time.sleep(random.random())
