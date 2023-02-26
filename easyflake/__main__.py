import functools
import sys
from typing import Optional

import click

from easyflake import config, logging


@click.group()
def cli():
    pass


def partial_option(*args, help="", default=None, **kwargs):
    if default is not None:
        help_arr = [help] if help else []
        help_arr.append(f"DEFAULT {default}")
        help = " ".join(help_arr)
    return click.option(*args, help=help, default=default, **kwargs)


def global_options(func):
    @click.option("--debug", "DEBUG", is_flag=True)
    @click.option("--no-color", "NO_COLOR", is_flag=True)
    @functools.wraps(func)
    def wrapper(*args, DEBUG: bool, NO_COLOR: bool, **kwargs):
        if DEBUG:
            config.DEBUG_MODE = True
        if not NO_COLOR:
            config.COLOR_MODE = True
        return func(*args, **kwargs)

    return wrapper  # type: ignore


@cli.command()
@global_options
@partial_option("-h", "--host", default="[::]")
@partial_option("-p", "--port", type=int, default=50051)
@partial_option("-d", "--daemon", "is_daemon", is_flag=True)
@partial_option("--pid-file")
def grpc(host: str, port: int, is_daemon: bool, pid_file: Optional[str]):
    """
    run gRPC server to get sequential node IDs.
    """
    # check if the command is available
    try:
        from easyflake.grpc.server import serve as grpc_serve
    except ImportError:
        msg = (
            "Failed to import some modules. "
            "If you want to run the gRPC server, execute `pip install easyflake[grpc]`"
        )
        logging.error(msg)
        sys.exit(1)

    # check daemon-related options
    if pid_file and not is_daemon:
        msg = (
            "If the --pid-file option is set, "
            "the -d or --daemon option must also be set to daemonize the server."
        )
        logging.error(msg)
        sys.exit(1)

    grpc_serve(host, port, is_daemon=is_daemon, pid_file=pid_file)


if __name__ == "__main__":
    cli()
