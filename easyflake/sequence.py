import math
from dataclasses import dataclass
from datetime import timedelta
from multiprocessing import Value
from multiprocessing.sharedctypes import Synchronized
from typing import TYPE_CHECKING, Dict, Set

from easyflake.clock import ClockScaler
from easyflake.exceptions import SequenceOverflowError

__all__ = [
    "TimeSequence",
    "TimeSequenceProvider",
    "SimpleSequencePool",
]


LOCK_TO = 2


@dataclass(frozen=True)
class TimeSequence:
    timestamp: int
    value: int


class TimeSequenceProvider:
    """A class for generating a sequence of numbers based on a time scale."""

    def __init__(self, bits: int, epoch: float, time_scale: int):
        """
        Args:
            bits (int): The bits of sequential ID.
            epoch (float): The base datetime to calculate the timestamp
            time_scale (int): The scale of the timestamp to use. The ID sequence will
                              be incremented at intervals determined by the scale.
        """
        self._bits = bits + 1

        self._sequence_max = 2**bits - 1
        self._sequence_mask = 2**self._bits - 1

        self._clock = ClockScaler(time_scale, epoch=epoch)

        _, val = self._attach_timestamp_to_value(0)
        if TYPE_CHECKING:
            self._shared: Synchronized[int]
        self._shared = Value("Q", val)  # type: ignore

    def get_required_bits(self, delta: timedelta):
        """
        Get the number of bits to represent given years, days, hours, minutes, seconds.
        """
        return math.floor(math.log(self._clock.future(delta), 2)) + 1

    def _attach_timestamp_to_value(self, value: int):
        current = self._clock.current()
        return current, (current << self._bits) | value

    def _detach_timestamp_from_value(self, value: int) -> int:
        return value & self._sequence_mask

    @property
    def last_updated_timestamp(self):
        """
        Get the timestamp of the last modification to the shared value.
        """
        return self._shared.value >> self._bits

    def next(self):
        """
        Get the next ID in the sequence at a specific time scale. When the ID reaches
        its maximum value, wait until the next tick before generating a new ID.
        """
        while True:
            with self._shared.get_lock():
                current = self._clock.current()
                future = self.last_updated_timestamp

                if current > future:
                    seq = 0
                    break
                seq = self._detach_timestamp_from_value(self._shared.value)
                if seq <= self._sequence_max:
                    break

            self._clock.sleep(current, future)

        timestamp, seq_with_timestamp = self._attach_timestamp_to_value(seq)
        self._shared.value = seq_with_timestamp + 1
        return TimeSequence(timestamp, seq)


class SimpleSequencePool:
    def __init__(self):
        self._pool: Dict[int, Set[int]] = {}

    def _init(self, bits: int):
        if bits not in self._pool:
            self._pool[bits] = {i for i in range(1 << bits)}

    def pop(self, bits: int):
        self._init(bits)
        try:
            return self._pool[bits].pop()
        except KeyError:
            raise SequenceOverflowError(bits)

    def rm(self, bits: int, seq: int):
        self._init(bits)
        self._pool[bits] = self._pool[bits] - {seq}

    def push(self, bits: int, seq: int):
        if not 0 <= seq < 2**bits:
            raise ValueError(f"sequence {seq} is too large on {bits} bits")
        self._pool[bits].add(seq)
