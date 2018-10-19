import pytest
import time

import threading

from simple_worker.queue import Queue
from simple_worker.queue_providers import MemoryProvider
from simple_worker.task_handler_registry import TaskHandlerRegistry
from simple_worker.worker import Worker


def test_start_and_shutdown(worker: Worker):
    def start_worker():
        worker.start()

    worker_thread = threading.Thread(target=start_worker)
    worker_thread.start()

    time.sleep(0.1)
    assert worker_thread.is_alive()

    worker.shutdown()

    worker_thread.join(timeout=0.1)
    assert not worker_thread.is_alive()


@pytest.mark.skip(reason="incomplete")
def test_performs_tasks(worker: Worker):
    def start_worker():
        worker.start()

    worker_thread = threading.Thread(target=start_worker)
    worker_thread.start()

    worker.shutdown()
    worker_thread.join(timeout=0.1)


task_handler_invocations = []


def dummy_task_handler(a, b):
    task_handler_invocations.append([a, b])
    return a + b


@pytest.fixture
def worker(task_handler_registry=None):
    queues = [Queue(provider=MemoryProvider(), queue_name='dummy_queue')]

    task_handler_registry = TaskHandlerRegistry()
    task_handler_registry.register('task1', dummy_task_handler)

    return Worker(
        queues=queues,
        task_handler_registry=task_handler_registry,
        task_executor_cls=None)
