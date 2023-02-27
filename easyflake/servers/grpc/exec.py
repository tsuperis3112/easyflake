import os
import signal
import socket
import sys
from concurrent import futures
from typing import Optional

import grpc
from grpc_health.v1 import health_pb2_grpc
from grpc_health.v1.health import HealthServicer
from lockfile.pidlockfile import PIDLockFile

from easyflake import config, logging
from easyflake.grpc import sequence_pb2_grpc

from .sequence import SequenceServicer


def serve(host: str, port: int, *, pid_file: Optional[str] = None):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        # check if the port is available.
        sock.bind(("localhost", port))

    pid_path = pid_file and os.path.abspath(pid_file)
    pid_lock_file = PIDLockFile(pid_path) if pid_path else None
    endpoint = f"{host}:{port}"

    if config.DAEMON_MODE:
        # work on background
        try:
            from daemon import DaemonContext
        except ImportError:
            logging.error("The daemon feature is not supported by your system.")
            sys.exit(1)

        with DaemonContext(pidfile=pid_lock_file):
            _serve(endpoint)
    else:
        # work on foreground
        try:
            if pid_lock_file is not None:
                pid_lock_file.acquire()
            _serve(endpoint)
        finally:
            if pid_lock_file is not None:
                pid_lock_file.release()


def _serve(endpoint: str):
    logging.success(f"start gRPC server => {endpoint}")

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    sequence_pb2_grpc.add_SequenceServicer_to_server(SequenceServicer(), server)
    health_pb2_grpc.add_HealthServicer_to_server(HealthServicer(), server)

    def signal_handler(sig, frame):
        logging.info("stopping server...")
        server.stop(1)

    server.add_insecure_port(endpoint)
    server.start()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    server.wait_for_termination()
