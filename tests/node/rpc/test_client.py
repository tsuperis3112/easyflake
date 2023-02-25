from unittest import TestCase
from unittest.mock import Mock, call, patch

from easyflake.node.rpc.client import ListenStatus, RpcClient


class TestGetConnectionID(TestCase):
    @patch("time.sleep")
    def test_connection_aborted(self, sleep: Mock):
        listen_called = 0

        def _listen_mock(self):
            nonlocal listen_called
            listen_called += 1
            # self._shared_status.value = ListenStatus.RUNNING
            self._channel = Mock()

        with patch("easyflake.node.rpc.client.RpcClient.listen", _listen_mock):
            client = RpcClient(endpoint="test", node_id_bits=10, retry=100)
            client.stop()
            with self.assertRaises(
                ConnectionAbortedError,
                msg="if connection is aborted, an error must be raised",
            ):
                client.get_connection_id()

        sleep.assert_called()
        self.assertListEqual(sleep.call_args_list, [call(0.5)])

        self.assertEqual(
            listen_called,
            2,
            "listen() should have been called in __init__() and get_connection_id()",
        )

    @patch("time.sleep")
    def test_timeout(self, sleep: Mock):
        listen_called = 0

        def _listen_mock(self):
            nonlocal listen_called
            listen_called += 1
            self._shared_status.value = ListenStatus.RUNNING

        with patch("easyflake.node.rpc.client.RpcClient.listen", _listen_mock):
            client = RpcClient(endpoint="test", node_id_bits=10, retry=4)
            with self.assertRaises(
                TimeoutError,
                msg="When the retry count reaches the max, an error must be raised",
            ):
                client.get_connection_id()

        sleep.assert_called()
        self.assertListEqual(
            sleep.call_args_list,
            [call(0.5), call(1.0), call(2.0)],
            "The number of retries is 4, so sleep should have been called 3 times.",
        )

        self.assertEqual(
            listen_called,
            1,
            "listen() should have been called in __init__()",
        )
