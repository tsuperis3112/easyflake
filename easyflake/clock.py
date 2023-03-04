import time
from datetime import timedelta


class Scale:
    SECOND = 0
    MILLI = 3
    MICRO = 6


class ClockScaler:
    def __init__(self, scale: int, epoch: float):
        """
        A clock that counts up with a certain scale factor.

        Args:
            scale (int): The scale factor for the clock. Must be between 0 and 6.
            epoch (float): The epoch timestamp.
        """
        if not Scale.SECOND <= scale <= Scale.MICRO:
            raise ValueError(f"Please set a scale between {Scale.SECOND} and {Scale.MICRO}.")
        self.scale_factor = 10**scale
        self.epoch = int(epoch * self.scale_factor)

    def current(self) -> int:
        """
        Return the current time elapsed since the start timestamp, expressed in the
        clock's units of measurement.
        """
        return int(time.time() * self.scale_factor) - self.epoch

    def future(self, delta: timedelta) -> int:
        return self.current() + int(delta.total_seconds() * self.scale_factor)

    def sleep(self, current: int, future: int):
        """Sleeps for a clock tick."""
        time.sleep((future - current) / self.scale_factor)
