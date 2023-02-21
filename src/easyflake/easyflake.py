from easyflake.clock import TimeScale
from easyflake.log import warn
from easyflake.sequence import TimeBasedSequenceGenerator

DEFAULT_EPOCH_TIMESTAMP = 1675891440


class EasyFlake:
    def __init__(
        self,
        node_id: int,  # TODO: auto generate
        node_id_bits: int = 8,
        sequence_bits: int = 10,
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
                                     Defaults to 2023-02-08 21:24:00.
            time_scale (int, optional): number of decimal places in timestamp.
        """
        max_node_id = (1 << node_id_bits) - 1
        if not 0 <= node_id <= max_node_id:
            raise ValueError(
                f"node_id is required >=0 and <={max_node_id}, but {node_id} is given."
            )

        self.node_id_bits = node_id_bits
        self.sequence_bits = sequence_bits

        self.node_id = node_id
        self.generator = TimeBasedSequenceGenerator(
            sequence_bits=sequence_bits,
            epoch=epoch,
            time_scale=time_scale,
            **kwargs,
        )

        # Check sufficient node_id bits
        if not self._has_sufficient_timestamp_bits(hours=1):
            raise ValueError("Unable to count timestamp within one hour.")
        if not self._has_sufficient_timestamp_bits(years=1):
            warn("Unable to count timestamp within a year.")

    def _has_sufficient_timestamp_bits(self, **duration):
        max_node_id_bits = 64 - self.generator.get_required_bits(**duration)
        return self.node_id_bits < max_node_id_bits

    def next_id(self):
        """
        generate next ID by current timestamp
        """
        seq = self.generator.get_next_id()
        return (
            (seq.timestamp << (self.sequence_bits + self.node_id_bits))
            | (self.node_id << self.sequence_bits)
            | seq.value
        )
