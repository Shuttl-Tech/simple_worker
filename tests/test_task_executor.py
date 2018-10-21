from contextlib import contextmanager

from simple_worker import TaskExecutor
from simple_worker import Task

invocations = []


def dummy_handler_fn(x):
    invocations.append(x)


def test_default_executor():
    invocations.clear()

    task = Task(name='test', payload={'x': 'x'})
    TaskExecutor(dummy_handler_fn).execute(task)

    assert len(invocations) == 1


executor_context_started = False
executor_context_ended = False


class ExecutorWithContext(TaskExecutor):
    @contextmanager
    def context(self):
        self.executor_context_started = True
        yield
        self.executor_context_ended = True

    def setup_test_vars(self):
        self.executor_context_started = False
        self.executor_context_ended = False


def test_executor_with_overridden_context():
    invocations.clear()

    executor = ExecutorWithContext(dummy_handler_fn)
    executor.setup_test_vars()
    assert not executor.executor_context_started
    assert not executor.executor_context_ended

    task = Task(name='test', payload={'x': 'x'})
    executor.execute(task)

    assert executor.executor_context_started
    assert executor.executor_context_ended
    assert len(invocations) == 1
