from unittest.mock import patch

from easyflake.node.random import RandomNodeFactory


def test_max_value():
    bits = 32
    factory = RandomNodeFactory()
    assert factory.get_node_id(bits) < (1 << bits)


def test_called_randbits():
    bits = 2
    expected = 3

    with patch("secrets.randbits", return_value=expected) as randbits_mock:
        factory = RandomNodeFactory()
        actual = factory.get_node_id(bits)
        assert actual == expected

        randbits_mock.assert_called_once_with(bits)
