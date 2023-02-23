from easyflake.clock import TimeScale
from easyflake.log import warn
from easyflake.sequence import TimeBasedSequenceGenerator

DEFAULT_EPOCH_TIMESTAMP = 1675859040


class EasyFlake:
    id_bits = 64

    def __init__(
        self,
        node_id: int,  # TODO: auto generate
        node_id_bits: int = 10,
        sequence_bits: int = 8,
        epoch: float = DEFAULT_EPOCH_TIMESTAMP,
        time_scale: int = TimeScale.MILLI,
        **kwargs,
    ):
        """
        Class for generating 64-bit IDs similar to Snowflake or Sonyflake.

        Args:
            node_id (int): node ID of execution environment
            node_id_bits (int, optional): maximum number of bits in node ID part.
            sequence_bits (int, optional): maximum number of bits in sequence ID part.
            epoch (float, optional): Timestamp that is used as a reference when
                                     generating bits of timestamp section.
                                     Defaults to 2023-02-08T12:24:00Z.
            time_scale (int, optional): number of decimal places in timestamp.
        """
        self.node_id_bits = node_id_bits
        self.sequence_bits = sequence_bits

        self.node_id = node_id

        self.sequence_generator = TimeBasedSequenceGenerator(
            bits=sequence_bits,
            epoch=epoch,
            time_scale=time_scale,
            **kwargs,
        )
        self._validate()

    def get_id(self):
        """generate next ID by current timestamp"""
        seq = self.sequence_generator.next()
        return (
            (seq.timestamp << (self.sequence_bits + self.node_id_bits))
            | (self.node_id << self.sequence_bits)
            | seq.value
        )

    def _validate(self):
        """validate attributes."""
        self._validate_sequence_bits()
        self._validate_node_id()
        self._validate_id_length()

    def _validate_node_id(self):
        if self.node_id_bits < 1:
            raise ValueError("node_id_bits is required to be >0")

        max_node_id = (1 << self.node_id_bits) - 1
        if not 0 <= self.node_id <= max_node_id:
            raise ValueError(
                f"node_id is required to be >=0 and <={max_node_id}, "
                f"but {self.node_id} is given."
            )

    def _validate_sequence_bits(self):
        if self.sequence_bits < 1:
            raise ValueError("sequence_bits is required to be >0")

    def _validate_id_length(self):
        # Check sufficient node_id bits
        if not self._has_sufficient_timestamp_bits(years=1):
            raise ValueError("Unable to count timestamp within a year.")
        if not self._has_sufficient_timestamp_bits(years=3):
            warn("Unable to count timestamp within 10 years.")

    def _has_sufficient_timestamp_bits(self, **duration):
        timestamp_bits = self.sequence_generator.get_required_bits(**duration)
        bits = timestamp_bits + self.node_id_bits + self.sequence_bits
        return bits < self.id_bits
