import math
import time


class TimeScale:
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
        self._initialize_timestamp = int(time.time() * self.scale_factor)

    def current(self) -> int:
        """
        Return the current time elapsed since the start timestamp, expressed in the
        clock's units of measurement.
        """
        return int(time.time() * self.scale_factor) - self._initialize_timestamp

    def sleep(self):
        """Sleeps for 1/10 clock tick."""
        time.sleep(0.1 / self.scale_factor)

    def bits_for_duration(self, years=0, days=0, hours=0, minutes=0, seconds=0) -> int:
        """
        Calculates the number of bits required to represent years in the clock's scale.
        """
        to = (
            seconds
            + minutes * 60
            + hours * 3600
            + days * 86400
            + years * 31536000
            + time.time()
        )
        duration = to * self.scale_factor - self.epoch
        return math.floor(math.log(duration, 2)) + 1

    def get_elapsed_time(self, scaled: int) -> int:
        """
        Converts a timestamp in the clock's scale to the elapsed time.

        Args:
            scaled (int): The scaled timestamp to convert.

        Returns:
            int: The real-world timestamp.
        """
        return scaled + self._initialize_timestamp - self.epoch
