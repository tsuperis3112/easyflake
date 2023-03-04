import functools
from typing import Callable, Optional

import click

from easyflake import config
from easyflake.node.grpc import NodeIdPool


@click.group()
@click.version_option()
def cli():
    pass


def partial_option(*args, help="", default=None, **kwargs):
    if default is not None:
        help_arr = [help] if help else []
        help_arr.append(f"DEFAULT {default}")
        help = " ".join(help_arr)
    return click.option(*args, help=help, default=default, **kwargs)


def global_options(
    func: Optional[Callable] = None,
    *,
    enable_debug=True,
    enable_no_color=True,
    enable_daemon=False,
):
    if func is None:
        return functools.partial(
            global_options,
            enable_debug=enable_debug,
            enable_no_color=enable_no_color,
            enable_daemon=enable_daemon,
        )

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # change global config
        config.DEBUG_MODE = kwargs.pop("DEBUG", False)
        config.COLOR_MODE = not kwargs.pop("NO_COLOR", False)
        config.DAEMON_MODE = kwargs.pop("DAEMON", False)
        return func(*args, **kwargs)

    # set options
    if enable_debug:
        wrapper = click.option("--debug", "DEBUG", is_flag=True)(wrapper)
    if enable_no_color:
        wrapper = click.option("--no-color", "NO_COLOR", is_flag=True)(wrapper)
    if enable_daemon:
        wrapper = click.option("-d", "--daemon", "DAEMON", is_flag=True)(wrapper)

    return wrapper


@cli.command()
@global_options(enable_daemon=True)
@partial_option("-h", "--host", default="[::]")
@partial_option("-p", "--port", type=int, default=50051)
@partial_option("--pid-file")
def grpc(host: str, port: int, pid_file: Optional[str]):
    """
    run gRPC server to get sequential node IDs.
    """
    # check if the command is available

    NodeIdPool.serve(host, port, pid_file=pid_file)


if __name__ == "__main__":
    cli()
