from unittest import TestCase
from unittest.mock import patch

from click.testing import CliRunner

from easyflake.__main__ import cli


class TestCLI(TestCase):
    def setUp(self):
        self.cmd = CliRunner()

    def test_grpc(self):
        with patch("easyflake.node.grpc.NodeIdPool.serve") as serve_mock:
            self.cmd.invoke(cli, args=["grpc"])

        serve_mock.assert_called_once()
