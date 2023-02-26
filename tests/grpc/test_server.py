from unittest import TestCase
from unittest.mock import patch

from grpc_testing import (
    Server,
    UnaryStreamServerRpc,
    server_from_dictionary,
    strict_real_time,
)

from easyflake.grpc.protobuf import sequence_pb2
from easyflake.grpc.server.servicers import SequenceOverflowError, SequenceServicer

service_descriptor = sequence_pb2.DESCRIPTOR.services_by_name["Sequence"]
method_descriptor = service_descriptor.methods_by_name["LiveStream"]


class TestSequenceServicer(TestCase):
    @staticmethod
    def _make_server(servicer: SequenceServicer) -> Server:
        """helper method to create a server from a servicer."""
        return server_from_dictionary(
            {service_descriptor: servicer}, time=strict_real_time()
        )

    @staticmethod
    def _get_rpc(
        server: Server, request: sequence_pb2.SequenceRequest
    ) -> UnaryStreamServerRpc:
        """helper method to get a UnaryStreamServerRpc object."""
        return server.invoke_unary_stream(method_descriptor, (), request, None)

    @patch("time.sleep")
    def test_live_stream(self, sleep):
        sleep.side_effect = StopIteration

        bits = 1
        server = self._make_server(SequenceServicer())
        request = sequence_pb2.SequenceRequest(bits=bits)

        # Test the live stream method.
        for i in range(2**bits):
            rpc = self._get_rpc(server, request)
            reply = rpc.take_response()
            self.assertEqual(
                reply.sequence,
                i,
                f"Unexpected sequence value: {reply.sequence} (expected: {i})",
            )

        # Test the case when the sequence reaches max.
        with self.assertRaises(ValueError) as cm:
            rpc = self._get_rpc(server, request)
            reply = rpc.take_response()
        self.assertIn("no more", str(cm.exception).lower(), "Unexpected error message")

    def test_take_response(self):
        servicer = SequenceServicer()

        bits = 4
        expected_max = 15

        # Test the take_sequence method.
        for expected_seq in range(expected_max + 1):
            seq = servicer.take_sequence(bits)
            self.assertEqual(
                seq,
                expected_seq,
                f"Unexpected sequence value: {seq} (expected: {expected_seq})",
            )

        # Test the case when the sequence reaches max.
        with self.assertRaises(SequenceOverflowError) as cm:
            servicer.take_sequence(bits)
        self.assertEqual(cm.exception.max_value, expected_max)

        # Test the cleanup_sequence method.
        expected = 4
        servicer.cleanup_sequence(bits, expected)
        seq = servicer.take_sequence(bits)
        self.assertEqual(
            seq,
            expected,
            f"Unexpected sequence value: {seq} (expected: {expected})",
        )
