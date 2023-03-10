import pytest

from easyflake.node.base import INVALID_VALUE, NodeIdPool


@pytest.fixture
def process_mock(mocker):
    class ProcessMock:
        def __init__(self, target, **kwargs):
            self.target = target

        def start(self):
            self.target()

    mocker.patch("multiprocessing.synchronize.Lock")
    return mocker.patch("multiprocessing.Process", side_effect=ProcessMock)


@pytest.fixture
def pool_class():
    class ConcreteNodeIdPool(NodeIdPool):
        def __init__(self, sequence: int):
            self._sequence = sequence
            super().__init__("endpoint", 10)

        def listen(self):
            if self._sequence == INVALID_VALUE:
                raise ValueError()
            yield self._sequence

    return ConcreteNodeIdPool


@pytest.fixture
def infinite_pool_class(pool_class):
    class ConcreteNodeIdInfinitePool(pool_class):
        def listen(self):
            while True:
                yield next(super().listen())

    return ConcreteNodeIdInfinitePool


def test_NodeIdPool_get(infinite_pool_class):
    pool = infinite_pool_class(1)
    assert pool.get() == 1


def test_NodeIdPool_get_timeout(mocker, infinite_pool_class):
    mocker.patch("multiprocessing.synchronize.Event.wait", return_value=False)

    pool = infinite_pool_class(1)
    with pytest.raises(TimeoutError):
        pool.get()


def test_NodeIdPool_get_connection_error(mocker, infinite_pool_class):
    mocker.patch("multiprocessing.synchronize.Event.wait", return_value=True)

    pool = infinite_pool_class(INVALID_VALUE)
    with pytest.raises(ConnectionError):
        pool.get()


def test_NodeIdPool_start(mocker, pool_class, process_mock):
    fail_mock = mocker.patch.object(pool_class, "fail")
    stop_mock = mocker.patch.object(pool_class, "stop")

    mocker.patch("time.sleep")

    pool = pool_class(1)
    pool.start()

    fail_mock.assert_not_called()
    stop_mock.assert_called()


def test_NodeIdPool_start_failed(mocker, pool_class, process_mock):
    fail_mock = mocker.patch.object(pool_class, "fail")
    stop_mock = mocker.patch.object(pool_class, "stop")

    mocker.patch("time.sleep")

    pool = pool_class(INVALID_VALUE)
    pool.start()

    fail_mock.assert_called()
    stop_mock.assert_called()


def test_NodeIdPool_start_stop_by_other_process(mocker, infinite_pool_class, process_mock):
    fail_mock = mocker.patch.object(infinite_pool_class, "fail")
    stop_mock = mocker.patch.object(infinite_pool_class, "stop")

    event_is_set_mock = mocker.patch("multiprocessing.synchronize.Event.is_set")
    event_is_set_mock.side_effect = [False, False]
    mocker.patch("time.sleep")

    pool = infinite_pool_class(1)
    pool.start()

    fail_mock.assert_not_called()
    stop_mock.assert_called()


def test_NodeIdPool_start_already_started(mocker, infinite_pool_class):
    process_mock = mocker.patch("multiprocessing.Process")
    mocker.patch("multiprocessing.synchronize.Event.is_set", return_value=True)

    pool = infinite_pool_class(1)
    pool.start()

    process_mock.assert_not_called()
