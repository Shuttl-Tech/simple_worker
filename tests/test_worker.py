import pytest
import time

import threading

from simple_worker.queue import Queue
from simple_worker.queue_providers import MemoryProvider
from simple_worker.task_handler_registry import TaskHandlerRegistry
from simple_worker.worker import Worker
from simple_worker.task import Task
from simple_worker.task_executor import TaskExecutor


def test_start_and_shutdown(worker: Worker):
    def start_worker():
        worker.start()

    worker_thread = threading.Thread(target=start_worker)
    worker_thread.start()

    worker.shutdown()

    worker_thread.join(timeout=0.1)
    assert not worker_thread.is_alive()


def test_performs_tasks(queue: Queue, worker_thread: threading.Thread):
    task_handler_invocations.clear()

    task = Task(name='task1', payload={'a': 1, 'b': 2})
    queue.add_task(task)

    time.sleep(0.01)
    assert task_handler_invocations == [[1, 2]]


task_handler_invocations = []


def dummy_task_handler(a, b):
    task_handler_invocations.append([a, b])


@pytest.fixture
def queue():
    return Queue(provider=MemoryProvider(), queue_name='dummy_queue')


@pytest.fixture
def worker(queue, task_handler_registry=None):
    task_handler_registry = TaskHandlerRegistry()
    task_handler_registry.register('task1', dummy_task_handler)

    return Worker(
        queues=[queue],
        task_handler_registry=task_handler_registry,
        task_executor_cls=TaskExecutor)


@pytest.fixture
def worker_thread(worker, queue):
    def start_worker():
        worker.start()

    worker_thread = threading.Thread(target=start_worker)
    worker_thread.start()

    time.sleep(0.01)
    assert worker_thread.is_alive()

    yield worker_thread

    worker.shutdown()
    worker_thread.join(timeout=0.01)
