# EasyFlake

[![Test passing](https://github.com/tsuperis/easyflake/actions/workflows/tests.yml/badge.svg)](https://github.com/tsuperis/easyflake/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/tsuperis/easyflake/branch/main/graph/badge.svg?token=3TIHGMYN1G)](https://codecov.io/gh/tsuperis/easyflake)
![PyPI](https://img.shields.io/pypi/v/easyflake)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/easyflake)
[![License](https://img.shields.io/github/license/tsuperis/easyflake)](https://github.com/tsuperis/easyflake/blob/main/LICENSE)

EasyFlake is a Python package for generating 64-bit IDs similar to Snowflake or Sonyflake. It provides a simple way to generate unique and sortable IDs that can be used as primary keys in databases, message queue messages, or other distributed systems.

## Installation

Install the latest version of EasyFlake using pip:

```bash
pip install easyflake
```

## Usage

To use EasyFlake, simply create an instance of the `EasyFlake` class, passing in a unique node ID:

```python
from easyflake import EasyFlake

ef = EasyFlake(node_id=1)
print(ef.get_id())
```

The `get_id()` method generates the next ID by the current timestamp. You can customize the number of bits used for the node ID and sequence ID parts, as well as the epoch timestamp and time scale.

```python
ef = EasyFlake(node_id=0, node_id_bits=4, sequence_bits=6)
print(ef.get_id())
```

### Arguments

* `node_id` (int): A unique ID for the current node. This ID should be between 0 and (2 ^ node_id_bits) - 1, where `node_id_bits` is an optional argument that defaults to 8.
* `node_id_bits` (int, optional): The maximum number of bits used to represent the node ID. This argument defaults to 8.
* `sequence_bits` (int, optional): The maximum number of bits used to represent the sequence number. This argument defaults to 10.
* `epoch` (float, optional): A timestamp used as a reference when generating the timestamp section of the ID. This argument defaults to 1675859040(2023-02-08T12:24:00Z).
* `time_scale` (int, optional): The number of decimal places used to represent the timestamp. This argument defaults to 3(milliseconds).

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/tsuperis/easyflake/blob/main/LICENSE) file for details.
