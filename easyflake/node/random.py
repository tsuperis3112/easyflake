import secrets

from easyflake.node.base import BaseNodeFactory


class RandomNodeFactory(BaseNodeFactory):
    def get_node_id(self, bits: int):
        return secrets.randbits(bits)
