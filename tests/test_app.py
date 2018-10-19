import pytest

from simple_worker import App
from simple_worker.task_handler_registry import TaskHandlerAlreadyRegistered
from simple_worker.task_handler_registry import TaskHandlerNotFound


def test_app_rejects_invalid_broker_url():
    with pytest.raises(ValueError):
        App(broker_url='dummy')


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


@pytest.fixture
def app():
    return App('memory://dummy')


@pytest.fixture
def app_with_task(app):
    @app.register_task_handler('dummy_task')
    def dummy_task(str_param):
        return 'testing' + str_param

    return app
