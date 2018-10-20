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
    success_task_invocations.clear()

    task = Task(name='task_success', payload={'a': 1, 'b': 2})
    queue.add_task(task)

    time.sleep(0.01)
    assert success_task_invocations == [[1, 2]]

    assert queue.get_pending_task_count() == 0
    assert queue.get_in_progress_task_count() == 0


def test_does_not_ack_failed_tasks(queue: Queue,
                                   worker_thread: threading.Thread):
    failure_task_invocations.clear()

    task = Task(name='task_failure', payload={'a': 1, 'b': 2})
    queue.add_task(task)

    time.sleep(0.01)
    assert failure_task_invocations == [[1, 2]]

    # The task should be reserved, so no pending tasks should be present
    assert queue.get_pending_task_count() == 0

    # Since the task wasn't acked, it should still be 'in-progress'.
    assert queue.get_in_progress_task_count() == 1


success_task_invocations = []


def success_task_handler(a, b):
    success_task_invocations.append([a, b])


failure_task_invocations = []


def failure_task_handler(a, b):
    failure_task_invocations.append([a, b])
    raise RuntimeError('task failed')


@pytest.fixture
def queue():
    return Queue(provider=MemoryProvider(), queue_name='dummy_queue')


@pytest.fixture
def worker(queue, task_handler_registry=None):
    task_handler_registry = TaskHandlerRegistry()
    task_handler_registry.register('task_success', success_task_handler)
    task_handler_registry.register('task_failure', failure_task_handler)

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
