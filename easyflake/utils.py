import functools
import os
import sys
from typing import Callable, Optional


def daemonize(f: Callable, pid_file: Optional[str] = None):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if pid := os.fork():
            if pid_file:
                with open(pid_file, "w") as fp:
                    fp.write(str(pid) + "\n")
            sys.exit()
        else:
            f(*args, **kwargs)

    return wrapper
