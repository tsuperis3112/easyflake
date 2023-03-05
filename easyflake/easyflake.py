from datetime import timedelta
from typing import Union

from easyflake.clock import Scale
from easyflake.logging import warning
from easyflake.node import BaseNodeIdPool
from easyflake.sequence import TimeSequenceProvider

DEFAULT_EPOCH_TIMESTAMP = 1675859040

UNSET = type("UNSET", (), {})


class EasyFlake:
    id_bits = 64

    def __init__(
        self,
        node_id: Union[int, BaseNodeIdPool],
        node_id_bits: int = 8,
        sequence_bits: int = 8,
        epoch: float = DEFAULT_EPOCH_TIMESTAMP,
        time_scale: int = Scale.MILLI,
        **kwargs,
    ):
        """
        Class for generating 64-bit IDs similar to Snowflake or Sonyflake.

        Args:
            node_id (int, NodeIdPool): node ID of execution environment.
            node_id_bits (int): maximum number of bits in node ID part.
            sequence_bits (int): maximum number of bits in sequence ID part.
            epoch (float): Timestamp that is used as a reference when generating bits of timestamp
                           section.
                           Defaults to 2023-02-08T12:24:00Z.
            time_scale (int): number of decimal places in timestamp.
        """
        self._node_id_bits = node_id_bits
        self._sequence_bits = sequence_bits

        if isinstance(node_id, BaseNodeIdPool):
            self._node_id_provider = node_id.get
        else:
            self._node_id_provider = lambda: node_id  # type: ignore

        self._sequence_provider = TimeSequenceProvider(
            bits=sequence_bits,
            epoch=epoch,
            time_scale=time_scale,
            **kwargs,
        )
        self._validate()

    @property
    def node_id(self):
        return self._node_id_provider()

    def get_id(self):
        """generate next ID by current timestamp"""
        seq = self._sequence_provider.next()
        return (
            (seq.timestamp << (self._sequence_bits + self._node_id_bits))
            | (self.node_id << self._sequence_bits)
            | seq.value
        )

    def _validate(self):
        """validate attributes."""
        self._validate_sequence_bits()
        self._validate_node_id()
        self._validate_id_length()

    def _validate_node_id(self):
        if self._node_id_bits < 1:
            raise ValueError("node_id_bits is required to be >0")  # pragma: nocover

        max_node_id = (1 << self._node_id_bits) - 1
        if not 0 <= self.node_id <= max_node_id:
            raise ValueError(
                f"node_id is required to be >=0 and <={max_node_id}, "
                f"but {self.node_id} is given."
            )

    def _validate_sequence_bits(self):
        if self._sequence_bits < 1:
            raise ValueError("sequence_bits is required to be >0")  # pragma: nocover

    def _validate_id_length(self):
        # Check sufficient node_id bits
        if not self._has_sufficient_timestamp_bits(years=1):
            raise ValueError("Unable to count timestamp within a year.")
        if not self._has_sufficient_timestamp_bits(years=3):
            warning("Unable to count timestamp within 3 years.")

    def _has_sufficient_timestamp_bits(self, years: int):
        delta = timedelta(days=365 * years)
        timestamp_bits = self._sequence_provider.get_required_bits(delta)
        bits = timestamp_bits + self._node_id_bits + self._sequence_bits
        return bits < self.id_bits
