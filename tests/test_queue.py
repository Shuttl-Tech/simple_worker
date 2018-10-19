import pytest

from simple_worker.queue import Queue, TaskIDNotFound
from simple_worker.queue_providers import MemoryProvider
from simple_worker.task import Task


def test_add_and_reserve_task(queue):
    task = Task(name='dummy_task', payload={'arg1': 'hey', 'arg2': 'hi'})
    queue.add_task(task)

    task_id, task = queue.reserve_task()
    assert task == task


def test_reserve_when_none_available(queue):
    assert queue.reserve_task() is None


def test_ack(queue):
    task = Task(name='dummy_task', payload={'arg1': 'hey', 'arg2': 'hi'})
    queue.add_task(task)

    task_id, task = queue.reserve_task()
    queue.ack_task(task_id)

    with pytest.raises(TaskIDNotFound):
        queue.ack_task(task_id)

    assert queue.reserve_task() is None


def test_add_reserve_ack_multiple(queue):
    task1 = Task(name='dummy_task', payload={'name': 'task1'})
    task2 = Task(name='dummy_task', payload={'name': 'task2'})
    task3 = Task(name='dummy_task', payload={'name': 'task3'})

    queue.add_task(task1)
    queue.add_task(task2)

    task_1_id, reserved_task = queue.reserve_task()
    assert reserved_task == task1

    # Adding a new task shouldn't affect already queued tasks
    queue.add_task(task3)

    task_2_id, reserved_task = queue.reserve_task()
    assert reserved_task == task2

    queue.ack_task(task_1_id)
    queue.ack_task(task_2_id)

    with pytest.raises(TaskIDNotFound):
        queue.ack_task(task_1_id)

    with pytest.raises(TaskIDNotFound):
        queue.ack_task(task_2_id)


@pytest.fixture
def queue():
    return Queue(MemoryProvider(), 'dummy_queue_name')
