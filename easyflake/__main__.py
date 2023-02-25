import sys
from typing import Optional

import click


@click.group()
def cli():
    pass


@cli.command()
@click.option("-h", "--host", default="[::]")
@click.option("-p", "--port", type=int, default=50051)
@click.option("-d", "--daemon", "is_daemon", is_flag=True)
@click.option("--pid-file")
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
        click.echo(click.style(msg, fg="red"))
        sys.exit(1)

    # check daemon-related options
    if pid_file is not None and not is_daemon:
        msg = (
            "If the --pid-file option is set, "
            "the -d or --daemon option must also be set to daemonize the server."
        )
        click.echo(click.style(msg, fg="red"))
        sys.exit(1)

    grpc_serve(host, port, is_daemon=is_daemon, pid_file=pid_file)


if __name__ == "__main__":
    cli()
