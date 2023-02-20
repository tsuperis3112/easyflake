from easyflake.clock import TimeScale
from easyflake.log import warn
from easyflake.sequence import TimeBasedSequenceGenerator

DEFAULT_TIMESTAMP_OFFSET = 1675891440


class EasyFlake:
    def __init__(
        self,
        node_id: int,  # TODO: auto generate
        node_id_bits=8,
        sequence_bits=10,
        timestamp_offset=DEFAULT_TIMESTAMP_OFFSET,
        time_scale=TimeScale.MILLI,
        **kwargs,
    ):
        """
        Class for generating 64-bit IDs similar to Snowflake or Sonyflake.

        Args:
            node_id (int): node ID of execution environment
            node_id_bits (int, optional): maximum number of bits in node ID part.
            sequence_bits (int, optional): maximum number of bits in sequence ID part. Defaults to 10.
            timestamp_offset (float, optional): Timestamp that is used as a reference when generating bits of
                                                timestamp section. Defaults to DEFAULT_TIMESTAMP_OFFSET.
            time_scale (int, optional): number of decimal places in timestamp. Defaults to TimeScale.MILLI.
        """
        max_machine_id = (1 << node_id_bits) - 1
        if not 0 <= node_id <= max_machine_id:
            raise ValueError(
                f"machine_id is required >=0 and <={max_machine_id}, but {node_id} is given."
            )

        self.machine_id_bits = node_id_bits
        self.sequence_bits = sequence_bits

        self.machine_id = node_id
        self.generator = TimeBasedSequenceGenerator(
            sequence_bits=sequence_bits,
            timestamp_offset=timestamp_offset,
            time_scale=time_scale,
            **kwargs,
        )

        # Check sufficient machine_id bits
        if not self._has_sufficient_timestamp_bits(hours=1):
            raise ValueError(
                "Unable to count timestamp within one hour."
                "Consider reducing the machine ID value or changing the time_scale to a greater precision."
            )

        if not self._has_sufficient_timestamp_bits(years=1):
            warn(
                "Unable to count timestamp within a year."
                "Consider reducing the machine ID value or changing the time_scale to a greater precision."
            )

    def _has_sufficient_timestamp_bits(self, **duration):
        max_machine_id_bits = 64 - self.generator.get_required_bits(**duration)
        return self.machine_id_bits < max_machine_id_bits

    def next_id(self):
        """
        generate next ID by current timestamp
        """
        seq = self.generator.get_next_id()
        return (
            (seq.timestamp << (self.sequence_bits + self.machine_id_bits))
            | (self.machine_id << self.sequence_bits)
            | seq.value
        )
