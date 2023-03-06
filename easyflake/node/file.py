import os
import re
import sys
import time
from dataclasses import dataclass, field
from typing import List, Optional

from lockfile import LockFile

from easyflake.exceptions import SequenceOverflowError
from easyflake.sequence import SimpleSequencePool

from .base import NodeIdPool as BaseNodeIdPool

SEP = ":"
LIFESPAN = 10


dataclass_kwargs = {"kw_only": True} if sys.version_info >= (3, 10) else {}


def _update_expire():
    return time.time() + LIFESPAN


@dataclass(**dataclass_kwargs)
class LineStruct:
    bits: int
    sequence: int
    expire: float = field(default_factory=_update_expire)

    _pattern = re.compile(rf"^(?P<bits>\d+){SEP}(?P<sequence>\d+){SEP}(?P<expire>\d+(?:\.\d+)?)$")

    @classmethod
    def parse(cls, line: str):
        match = cls._pattern.search(line.strip())
        if match is None:
            return None

        bits = int(match.group("bits"))
        sequence = int(match.group("sequence"))
        expire = float(match.group("expire"))
        return cls(bits=bits, sequence=sequence, expire=expire)

    def join(self):
        return SEP.join([str(self.bits), str(self.sequence), str(self.expire)])

    def update(self):
        self.expire = _update_expire()


class NodeIdPool(BaseNodeIdPool):
    def listen(self):
        sequence = None

        while True:
            with LockFile(self.endpoint):
                pool = SimpleSequencePool()
                new_lines = self._readlines(pool, sequence)

                if sequence is None:
                    # generate new sequence
                    try:
                        sequence = pool.pop(self.bits)
                        line = LineStruct(bits=self.bits, sequence=sequence)
                        new_lines.append(line.join())
                    except SequenceOverflowError:
                        pass

                with open(self.endpoint, "w+") as f:
                    f.write(os.linesep.join(new_lines))

            yield sequence

    def _readlines(self, pool: SimpleSequencePool, update_sequence: Optional[int]) -> List[str]:
        new_lines: List[str] = []

        with open(self.endpoint, "a+") as f:
            f.seek(0)
            while l := f.readline():  # noqa: E741
                now = time.time()
                line = LineStruct.parse(l)
                if line is None or now > line.expire:
                    # remove line
                    continue

                if line.bits == self.bits:
                    pool.rm(line.bits, line.sequence)
                    if line.sequence == update_sequence:
                        # prolong line's lifespan
                        line.update()
                new_lines.append(line.join())

        return new_lines
