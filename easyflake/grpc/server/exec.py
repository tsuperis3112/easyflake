import os
import signal
import socket
import sys
from concurrent import futures
from typing import Optional

import grpc
from lockfile.pidlockfile import PIDLockFile

from easyflake import config, logging
from easyflake.grpc.protobuf import sequence_pb2_grpc

from .servicers import SequenceServicer


def serve(
    host: str,
    port: int,
    *,
    is_daemon=False,
    pid_file: Optional[str] = None,
):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        # check if the port is available.
        sock.bind(("localhost", port))

    endpoint = f"{host}:{port}"

    if is_daemon:
        try:
            from daemon import DaemonContext
        except ImportError:
            logging.error("The daemon feature is not supported by your system.")
            sys.exit(1)

        pid_path = pid_file and os.path.abspath(pid_file)
        pid_lock_file = PIDLockFile(pid_path) if pid_path else None
        with DaemonContext(pidfile=pid_lock_file):
            config.DAEMON_MODE = True
            _serve(endpoint)
    else:
        _serve(endpoint)


def _serve(endpoint: str):
    logging.success(f"start gRPC server => {endpoint}")

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
    sequence_pb2_grpc.add_SequenceServicer_to_server(SequenceServicer(), server)

    server.add_insecure_port(endpoint)

    def signal_handler(sig, frame):
        logging.info("stopping server...")
        server.stop(0)

    server.start()
    signal.signal(signal.SIGTERM, signal_handler)

    server.wait_for_termination()
