from unittest import TestCase
from unittest.mock import patch

from easyflake.node.rpc import RpcNodeFactory


class TestGetNodeID(TestCase):
    @patch("easyflake.node.rpc.factory.RpcClient")
    @patch("easyflake.node.rpc.factory.RpcNodeFactory.get_client")
    def test_failed_get_node_id_with_timeout(self, get_client, client):
        client.get_connection_id.side_effect = TimeoutError()
        get_client.return_value = client

        factory = RpcNodeFactory("endpoint")

        with self.assertRaises(
            TimeoutError,
            msg="TimeoutError must be raised when get_connection_id times out",
        ):
            factory.get_node_id(0)

        client.listen.assert_not_called()

    @patch("easyflake.node.rpc.factory.RpcClient")
    @patch("easyflake.node.rpc.factory.RpcNodeFactory.get_client")
    def test_failed_get_node_id_with_error(self, get_client, client):
        expected_error_classes = [ConnectionAbortedError, TimeoutError]

        client.get_connection_id.side_effect = expected_error_classes
        get_client.return_value = client

        factory = RpcNodeFactory("endpoint")

        for err in expected_error_classes:
            with self.assertRaises(err):
                factory.get_node_id(0)

    @patch("easyflake.node.rpc.factory.RpcClient")
    @patch("easyflake.node.rpc.factory.RpcNodeFactory.get_client")
    def test_success_get_node_id_with_connection_aborted(self, get_client, client):
        expected1, expected2 = 11, 22

        client.get_connection_id.side_effect = [
            expected1,
            ConnectionAbortedError(),
            expected2,
            ConnectionAbortedError(),
        ]
        get_client.return_value = client

        factory = RpcNodeFactory("endpoint")

        for expected in [expected1, expected2]:
            factory.get_node_id(0)
            actual = factory.get_node_id(0)
            self.assertEqual(actual, expected)
