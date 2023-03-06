import pytest

from easyflake.node.base import INVALID_VALUE, NodeIdPool


class ConcreteNodeIdPool(NodeIdPool):
    def __init__(self, sequence: int):
        self._sequence = sequence
        super().__init__("endpoint", 10)

    def listen(self):
        if self._sequence == INVALID_VALUE:
            raise ValueError()
        yield self._sequence


class ConcreteNodeIdInfinitePool(ConcreteNodeIdPool):
    def listen(self):
        while True:
            yield next(super().listen())


def test_NodeIdPool_get():
    pool = ConcreteNodeIdInfinitePool(1)
    assert pool.get() == 1


def test_NodeIdPool_get_timeout(mocker):
    mocker.patch("multiprocessing.synchronize.Event.wait", return_value=False)

    pool = ConcreteNodeIdInfinitePool(1)
    with pytest.raises(TimeoutError):
        pool.get()


def test_NodeIdPool_get_connection_error(mocker):
    mocker.patch("multiprocessing.synchronize.Event.wait", return_value=True)

    pool = ConcreteNodeIdInfinitePool(INVALID_VALUE)
    with pytest.raises(ConnectionError):
        pool.get()


def test_NodeIdPool_start(mocker):
    fail_mock = mocker.patch.object(ConcreteNodeIdPool, "fail")
    stop_mock = mocker.patch.object(ConcreteNodeIdPool, "stop")

    class ProcessMock:
        def __init__(self, target, **kwargs):
            self.target = target

        def start(self):
            self.target()

    mocker.patch("multiprocessing.Process", side_effect=ProcessMock)
    mocker.patch("multiprocessing.Lock")
    mocker.patch("time.sleep")

    pool = ConcreteNodeIdPool(1)
    pool.start()

    fail_mock.assert_not_called()
    stop_mock.assert_called()


def test_NodeIdPool_start_failed(mocker):
    fail_mock = mocker.patch.object(ConcreteNodeIdPool, "fail")
    stop_mock = mocker.patch.object(ConcreteNodeIdPool, "stop")

    class ProcessMock:
        def __init__(self, target, **kwargs):
            self.target = target

        def start(self):
            self.target()

    mocker.patch("multiprocessing.Process", side_effect=ProcessMock)
    mocker.patch("multiprocessing.Lock")
    mocker.patch("time.sleep")

    pool = ConcreteNodeIdPool(INVALID_VALUE)
    pool.start()

    fail_mock.assert_called()
    stop_mock.assert_called()


def test_NodeIdPool_start_stop_by_other_process(mocker):
    fail_mock = mocker.patch.object(ConcreteNodeIdInfinitePool, "fail")
    stop_mock = mocker.patch.object(ConcreteNodeIdInfinitePool, "stop")

    class ProcessMock:
        def __init__(self, target, **kwargs):
            self.target = target

        def start(self):
            self.target()

    mocker.patch("multiprocessing.Process", side_effect=ProcessMock)
    mocker.patch("multiprocessing.Lock")
    event_is_set_mock = mocker.patch("multiprocessing.synchronize.Event.is_set")
    event_is_set_mock.side_effect = [False, False]
    mocker.patch("time.sleep")

    pool = ConcreteNodeIdInfinitePool(1)
    pool.start()

    fail_mock.assert_not_called()
    stop_mock.assert_called()


def test_NodeIdPool_start_already_started(mocker):
    process_mock = mocker.patch("multiprocessing.Process")
    mocker.patch("multiprocessing.synchronize.Event.is_set", return_value=True)

    pool = ConcreteNodeIdInfinitePool(1)
    pool.start()

    process_mock.assert_not_called()
