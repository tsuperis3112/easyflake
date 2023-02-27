import time
from datetime import timedelta
from unittest import TestCase
from unittest.mock import patch

from freezegun import freeze_time

from easyflake.providers import TimeBasedSequence, TimeBasedSequenceProvider


class TestTimeBasedSequenceProvider(TestCase):
    @freeze_time("2023-02-08 00:00:00")
    def test_get_required_bits(self):
        seq = TimeBasedSequenceProvider(bits=2, epoch=time.time(), time_scale=2)

        # 10.23
        with freeze_time("2023-02-08 00:00:01.231"):
            actual = seq.get_required_bits(timedelta(seconds=9))
            expected = 10  # 1023
            self.assertEqual(actual, expected, "1023 (10.23sec) requires 10 bits.")

        # 10.24
        with freeze_time("2023-02-08 00:00:00.24"):
            actual = seq.get_required_bits(timedelta(seconds=10))
            expected = 11  # 1024
            self.assertEqual(actual, expected, "1024 (10.24sec) requires 11 bits.")

    @freeze_time("2023-02-08 12:24:12.345")
    def test_next_sequential_ids(self):
        with freeze_time("2023-02-08 12:24:00"):
            seq = TimeBasedSequenceProvider(bits=1, epoch=time.time(), time_scale=2)

        with patch("time.sleep", side_effect=[None, StopIteration]) as sleep_mock:
            # Generate two IDs and check if they are equal to the expected IDs
            for i in range(2):
                msg = f"ID generated ({i} times) is not equal to expected"
                expected = TimeBasedSequence(timestamp=1234, value=i)
                self.assertEqual(seq.next(), expected, msg)
            sleep_mock.assert_not_called()

            # Verify that a sleep is called when the sequence reaches the maximum value
            with self.assertRaises(StopIteration):
                with freeze_time("2023-02-08 12:24:12.346Z"):
                    seq.next()
            sleep_mock.assert_called()

        with patch("time.sleep", side_effect=StopIteration) as sleep_mock:
            # Generate an ID after 1 unit time
            with freeze_time("2023-02-08 12:24:12.35Z"):
                msg = "ID generated after 1 unit time is not equal to expected ID"
                expected = TimeBasedSequence(timestamp=1235, value=0)
                self.assertEqual(seq.next(), expected, msg)

            sleep_mock.assert_not_called()
