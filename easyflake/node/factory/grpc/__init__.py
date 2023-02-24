from typing import Dict

from easyflake.node.factory.base import BaseNodeFactory as BaseNodeFactory

from .client import Client


class gRpcNodeFactory(BaseNodeFactory):
    def __init__(self, endpoint: str):
        self._endpoint = endpoint
        self._clients: Dict[int, Client] = {}

    def _get_client(self, bits: int):
        if bits not in self._clients:
            self._clients[bits] = Client(self._endpoint, bits)
        return self._clients[bits]

    def get_id(self, bits: int):
        client = self._get_client(bits)
        return client.get_sequence()
