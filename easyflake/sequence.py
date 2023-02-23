import threading
from dataclasses import dataclass
from multiprocessing import Value
from multiprocessing.sharedctypes import Synchronized
from typing import TYPE_CHECKING

from easyflake.clock import ScaledClock


class _DummyLock:
    """A dummy lock class that does nothing."""

    def __init__(self, _=None, val=None):
        self.value: int = val or 0

    def __enter__(self):
        """dummy enter"""
        pass

    def __exit__(self, *args, **kwargs):
        """dummy exit"""
        pass

    def get_lock(self):
        return self


@dataclass(frozen=True)
class TimeBasedSequence:
    timestamp: int
    value: int


class TimeBasedSequenceGenerator:
    """A class for generating a sequence of numbers based on a time scale."""

    def __init__(
        self,
        bits: int,
        epoch: float,
        time_scale: int,
        use_multithread=True,
        use_multiproc=True,
    ):
        """
        Args:
            bits (int): The bits of sequential ID.
            epoch (float): The base datetime to calculate the timestamp
            time_scale (int): The scale of the timestamp to use. The ID sequence will
                              be incremented at intervals determined by the scale.
            use_multithread (bool): Whether to use a multi-threaded lock.
            use_multiproc (bool): Whether to use a multi-process lock.
        """
        self._bits = bits + 1

        self._sequence_max = 2**bits - 1
        self._sequence_mask = 2**self._bits - 1

        self._clock = ScaledClock(time_scale, epoch=epoch)

        if TYPE_CHECKING:
            self._shared: Synchronized[int]
        _, val = self._attach_timestamp_to_value(0)
        self._shared = (
            Value("Q", val) if use_multiproc else _DummyLock()  # type: ignore
        )
        self._thread_lock = threading.Lock() if use_multithread else _DummyLock()

    def get_required_bits(self, **duration):
        """
        Get the number of bits to represent given years, days, hours, minutes, seconds.
        """
        return self._clock.bits_for_duration(**duration)

    def _attach_timestamp_to_value(self, value: int):
        current = self._clock.current()
        timestamp = self._clock.get_elapsed_time(current)
        return timestamp, (current << self._bits) | value

    def _detach_timestamp_from_value(self, value: int) -> int:
        return value & self._sequence_mask

    @property
    def last_updated_timestamp(self):
        """
        Get the timestamp of the last modification to the shared value.

        Returns:
            int: The timestamp of the last modification to the shared value.
        """
        return self._shared.value >> self._bits

    def _new_sequence(self, seq: int):
        """
        Sets the shared value to the specified `value` and returns the current
        timestamp along with the set value.

        Args:
            seq (int): The value to set the shared value to.

        Returns:
            TimeBasedSequence: sequence ID with timestamp.

        Raises:
            ValueError: If `value` exceeds the maximum value allowed.
        """
        if seq > self._sequence_max:
            raise ValueError(
                f"value ({seq}) exceeds the maximum value ({self._sequence_max})"
            )

        timestamp, seq_with_timestamp = self._attach_timestamp_to_value(seq)
        self._shared.value = seq_with_timestamp + 1

        return TimeBasedSequence(timestamp, seq)

    def next(self):
        """
        Get the next ID in the sequence at a specific time scale. When the ID reaches
        its maximum value, wait until the next tick before generating a new ID.

        Returns:
            int: The next ID in the sequence.
        """
        with self._thread_lock:
            with self._shared.get_lock():
                return self._next()

    def _next(self):
        while True:
            current_timestamp = self._clock.current()
            next_timestamp = self.last_updated_timestamp + 1

            if current_timestamp >= next_timestamp:
                return self._new_sequence(0)

            seq = self._detach_timestamp_from_value(self._shared.value)
            if seq <= self._sequence_max:
                return self._new_sequence(seq)

            self._clock.sleep()
