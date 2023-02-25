import sys
from unittest import TestCase
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from easyflake.__main__ import cli


class CliTest(TestCase):
    def setUp(self):
        self.cmd = CliRunner()

    def test_grpc(self):
        with patch("easyflake.grpc.server.serve") as serve_mock:
            self.cmd.invoke(cli, args=["grpc"])

        serve_mock.assert_called_once()

    def test_grpc_import_error(self):
        sys.modules["easyflake.grpc.server"] = MagicMock(spec=[])
        try:
            result = self.cmd.invoke(cli, args=["grpc"])
            self.assertIn("pip install easyflake[grpc]", result.output)
            self.assertEqual(result.exit_code, 1)
        finally:
            del sys.modules["easyflake.grpc.server"]

    def test_grpc_invalid_options(self):
        with patch("easyflake.grpc.server.serve") as serve_mock:
            result = self.cmd.invoke(cli, args=["grpc", "--pid-file", "test.pid"])
            self.assertEqual(result.exit_code, 1)

        serve_mock.assert_not_called()
