#!/usr/bin/env python3

import os
import re

from grpc_tools import protoc

input_directory = "./easyflake/grpc/protos"
output_directory = "./easyflake/grpc"


def main():
    # codegen
    input_files = os.listdir(input_directory)
    protoc.main(
        (
            "",
            f"-I{input_directory}",
            f"--python_out={output_directory}",
            f"--pyi_out={output_directory}",
            f"--grpc_python_out={output_directory}",
            *input_files,
        )
    )

    # patch: relative import
    output_files = os.listdir(output_directory)
    for f in output_files:
        target = os.path.join(output_directory, f)
        if target.startswith("_") or os.path.isdir(target):
            # skip directory hidden files or directories
            continue

        with open(target, "r+") as fp:
            content = re.sub(
                r"^(import \S+_pb2 as \S+_pb2)$",
                r"from easyflake.grpc \1",
                fp.read(),
                flags=re.MULTILINE,
            )
            fp.seek(0)
            fp.write(content)


if __name__ == "__main__":
    main()
