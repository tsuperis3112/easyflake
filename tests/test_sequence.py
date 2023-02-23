import time
from unittest import TestCase
from unittest.mock import patch

from freezegun import freeze_time

from easyflake.sequence import TimeBasedSequence, TimeBasedSequenceGenerator


class TestTimeBasedSequenceGenerator(TestCase):
    @freeze_time("2023-02-08 12:24:12.345")
    def test_next_sequential_ids(self):
        with freeze_time("2023-02-08 12:24:00"):
            seq = TimeBasedSequenceGenerator(bits=1, epoch=time.time(), time_scale=2)

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
