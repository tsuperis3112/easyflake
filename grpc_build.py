#!/usr/bin/env python3
import os

from grpc_tools import protoc

input_directory = "./protos"
output_directory = "./easyflake/grpc"


def main():
    files = os.listdir(input_directory)

    protoc.main(
        (
            "",
            f"-I{input_directory}",
            f"--python_out={output_directory}",
            f"--grpc_python_out={output_directory}",
            *files,
        )
    )


if __name__ == "__main__":
    main()
