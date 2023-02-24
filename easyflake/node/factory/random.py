import secrets

from easyflake.node.factory.base import BaseNodeFactory


class RandomNodeFactory(BaseNodeFactory):
    def get_id(self, bits: int):
        return secrets.randbits(bits)
