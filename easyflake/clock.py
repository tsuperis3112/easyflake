import time
from datetime import timedelta
from enum import IntEnum


class TimeScale(IntEnum):
    SECOND = 0
    MILLI = 3
    MICRO = 6


class ScaledClock:
    def __init__(self, scale: int, epoch: float):
        """
        A clock that counts up with a certain scale factor.

        Args:
            scale (int): The scale factor for the clock. Must be between 0 and 6.
            epoch (float): The epoch timestamp.
        """
        if not TimeScale.SECOND <= scale <= TimeScale.MICRO:
            raise ValueError(
                f"Please set a scale between {TimeScale.SECOND} and {TimeScale.MICRO}."
            )
        self.scale_factor = 10**scale
        self.epoch = int(epoch * self.scale_factor)

    def current(self) -> int:
        return int(time.time() * self.scale_factor) - self.epoch

    def future(self, delta: timedelta) -> int:
        return self.current() + int(delta.total_seconds() * self.scale_factor)

    def sleep(self, current: int, future: int):
        time.sleep((future - current) / self.scale_factor)
