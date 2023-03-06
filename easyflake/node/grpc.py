import asyncio
import multiprocessing
import os
import signal
import socket
import sys
from concurrent import futures
from typing import Optional

import grpc
from grpc import StatusCode
from grpc_health.v1 import health_pb2_grpc
from grpc_health.v1.health import HealthServicer
from lockfile.pidlockfile import PIDLockFile

from easyflake import config, logging
from easyflake.exceptions import SequenceOverflowError
from easyflake.grpc import sequence_pb2, sequence_pb2_grpc
from easyflake.grpc.sequence_pb2 import SequenceReply, SequenceRequest
from easyflake.grpc.sequence_pb2_grpc import SequenceStub
from easyflake.sequence import SimpleSequencePool
from easyflake.utils.contextlib import ContextStackManager

from .base import NodeIdPool as BaseNodeIdPool


class NodeIdPool(BaseNodeIdPool):
    def listen(self):
        request = SequenceRequest(bits=self.bits)

        # Attempt to retrieve connection ID from the server
        while True:
            try:
                reply: SequenceReply
                for reply in self._connection.LiveStream(request):
                    yield reply.sequence

            except Exception as e:
                if isinstance(e, grpc.Call):
                    code = e.code()
                    if code == StatusCode.UNAVAILABLE:
                        logging.error("Connection to server is closed")

                    if code == StatusCode.CANCELLED:
                        return

                    if code == StatusCode.OUT_OF_RANGE:
                        yield None
                        continue

                raise

    @property
    def _connection(self):
        self._channel = grpc.insecure_channel(self.endpoint)
        return SequenceStub(self._channel)

    @classmethod
    def serve(cls, host: str, port: int, *, pid_file: Optional[str] = None):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # check if the port is available.
            sock.bind(("localhost", port))

        pid_path = pid_file and os.path.abspath(pid_file)
        context_manager = ContextStackManager(PIDLockFile(pid_path) if pid_path else None)

        endpoint = f"{host}:{port}"

        if config.DAEMON_MODE:
            # work on background
            try:
                from daemon import DaemonContext
            except ImportError:
                logging.error("The daemon feature is not supported by your system.")
                sys.exit(1)
            context_manager = DaemonContext(pidfile=context_manager)

        with context_manager:
            asyncio.run(cls._serve(endpoint))

    @staticmethod
    def _stop_server_signal(server: grpc.aio.Server):
        async def signal_handler():
            logging.info("stopping server")
            await server.stop(0)

        def handler(*args, **kwargs):
            asyncio.create_task(signal_handler())

        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            if not sys.platform.startswith("win"):
                loop.add_signal_handler(sig, handler)
            else:  # for Windows
                signal.signal(sig, handler)

    @classmethod
    async def _serve(cls, endpoint: str):
        logging.success(f"start gRPC server => {endpoint}")

        grpc.aio.init_grpc_aio()
        server = grpc.aio.server(futures.ThreadPoolExecutor())
        sequence_pb2_grpc.add_SequenceServicer_to_server(SequenceServicer(), server)
        health_pb2_grpc.add_HealthServicer_to_server(HealthServicer(), server)

        server.add_insecure_port(endpoint)
        await server.start()

        cls._stop_server_signal(server)

        await server.wait_for_termination()


class SequenceServicer(sequence_pb2_grpc.SequenceServicer):
    def __init__(self):
        self._sequence_pool = SimpleSequencePool()
        self._lock = multiprocessing.Lock()

    async def LiveStream(
        self, request: sequence_pb2.SequenceRequest, context: grpc.aio.ServicerContext
    ):
        bits = request.bits
        try:
            with self._lock:
                sequence = self._sequence_pool.pop(bits)
            logging.debug("connection %s is established", sequence)

        except SequenceOverflowError as e:
            await context.abort(grpc.StatusCode.OUT_OF_RANGE, str(e))
            return

        # wait unless connection is closed
        try:
            while True:
                yield sequence_pb2.SequenceReply(sequence=sequence)
        finally:
            logging.debug("connection %s is closed", sequence)
            with self._lock:
                self._sequence_pool.push(bits, sequence)
