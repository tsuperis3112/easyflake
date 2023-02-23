from unittest import TestCase
from unittest.mock import patch

from freezegun import freeze_time

from easyflake import EasyFlake, TimeScale
from easyflake.sequence import TimeBasedSequence


class TestEasyFlake(TestCase):
    @freeze_time("2022-03-01")
    def test_get_id(self):
        timestamp = 123
        node_id = 456
        sequence = TimeBasedSequence(timestamp=timestamp, value=789)

        ef = EasyFlake(node_id=node_id, node_id_bits=10, sequence_bits=9)
        with patch(
            "easyflake.sequence.TimeBasedSequenceGenerator.next", return_value=sequence
        ):
            self.assertEqual(
                ef.get_id(), timestamp << 19 | node_id << 9 | sequence.value
            )

    def test_max_node_id(self):
        common_args = {
            "node_id": 0,
            "node_id_bits": 10,
            "sequence_bits": 10,
            "time_scale": TimeScale.SECOND,
        }

        with patch("easyflake.clock.ScaledClock.bits_for_duration", return_value=43):
            EasyFlake(**common_args)

        with patch("easyflake.clock.ScaledClock.bits_for_duration", return_value=44):
            with self.assertRaises(ValueError):
                EasyFlake(**common_args)
