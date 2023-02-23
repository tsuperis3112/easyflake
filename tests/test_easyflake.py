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
            expected_id = timestamp << 19 | node_id << 9 | sequence.value
            actual_id = ef.get_id()
            msg = f"Generated ID {actual_id} is not equal to expected ID {expected_id}."
            self.assertEqual(actual_id, expected_id, msg)

    def test_instance_critical_lifetime(self):
        common_args = {
            "node_id_bits": 10,
            "sequence_bits": 10,
            "time_scale": TimeScale.SECOND,
        }

        # not dangerous lifetime
        with patch("easyflake.clock.ScaledClock.bits_for_duration", return_value=43):
            EasyFlake(**common_args)

        with patch("easyflake.clock.ScaledClock.bits_for_duration", return_value=44):
            msg = "The ValueError should be raised for dangerous lifetime."
            with self.assertRaises(ValueError, msg=msg):
                EasyFlake(**common_args)

    def test_instance_dangerous_lifetime(self):
        common_args = {
            "node_id_bits": 10,
            "sequence_bits": 10,
            "time_scale": TimeScale.SECOND,
        }

        with patch("easyflake.clock.ScaledClock.bits_for_duration") as clock_mock:
            clock_mock.side_effect = lambda years: 43 if years == 1 else 44

            # Assert that a warning is logged for dangerous lifetime
            with patch("easyflake.easyflake.warn") as warn_mock:
                EasyFlake(**common_args)
            warn_mock.assert_called_once()

    def test_invalid_node_id(self):
        with self.assertRaises(ValueError) as cm:
            EasyFlake(node_id=1024, node_id_bits=10)

        msg = "The error message should indicate that the node_id is invalid."
        self.assertIn("node_id", str(cm.exception), msg)
        self.assertIn("<=1023", str(cm.exception), "The error reason is not valid.")
