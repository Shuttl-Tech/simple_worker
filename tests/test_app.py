import pytest

from simple_worker import App
from simple_worker.task_handler_registry import TaskHandlerAlreadyRegistered
from simple_worker.task_handler_registry import TaskHandlerNotFound
from simple_worker.queue_providers import MemoryProvider, SQSProvider
from simple_worker.worker import Worker


def test_init():
    app = App()
    assert isinstance(app._queue_provider, SQSProvider)


def test_init_with_testing_mode():
    app = App(testing_mode=True)
    assert isinstance(app._queue_provider, MemoryProvider)


@pytest.mark.skip(reason='paul is lazy')
def test_queue_prefix():
    pass


def test_register_task_handler(app):
    @app.register_task_handler('task1')
    def task_1():
        return 'testing'

    with pytest.raises(TaskHandlerAlreadyRegistered):

        @app.register_task_handler('task1')
        def task_2():
            return 'testing'


def test_add_task_not_registered(app):
    with pytest.raises(TaskHandlerNotFound):
        app.add_task('task2')


def test_add_task(app_with_task):
    app_with_task.add_task('dummy_task')
    app_with_task.add_task('dummy_task')


@pytest.mark.skip(reason='Not implemented')
def test_add_task_validates_signature():
    pass


def test_worker(app):
    assert isinstance(app.worker(), Worker)


@pytest.fixture
def app():
    return App(testing_mode=True)


@pytest.fixture
def app_with_task(app):
    @app.register_task_handler('dummy_task')
    def dummy_task(str_param):
        return 'testing' + str_param

    return app
