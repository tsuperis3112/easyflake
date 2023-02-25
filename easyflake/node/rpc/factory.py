from typing import Dict, Optional

from easyflake.node.base import BaseNodeFactory as BaseNodeFactory

from .client import RpcClient


class RpcNodeFactory(BaseNodeFactory):
    def __init__(self, endpoint: str):
        self._endpoint = endpoint
        self._clients: Dict[int, RpcClient] = {}
        self._node_id: Optional[int] = None

    def get_client(self, bits: int):
        if bits not in self._clients:
            self._clients[bits] = RpcClient(self._endpoint, bits)
        return self._clients[bits]

    def get_node_id(self, bits: int) -> int:
        client = self.get_client(bits)
        try:
            self._node_id = client.get_connection_id()
        except (TimeoutError, ConnectionAbortedError):
            if self._node_id is None:
                raise

        return self._node_id  # type: ignore
