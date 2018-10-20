import json

from simple_worker.task import Task
from simple_worker.queue_providers import MessageIDNotFound


class TaskIDNotFound(Exception):
    pass


class Queue:
    def __init__(self, provider, queue_name):
        self._provider = provider
        self.name = queue_name

    def add_task(self, task):
        """
        Adds a task to the queue
        """
        message = serialize(task)
        self._provider.add(self.name, message)

    def reserve_task(self):
        """
        Reserves a task from the queue, returns a tuple of (task_id, task).

        task_id can be used to `ack` the task after processing
        """
        reserved = self._provider.reserve_one(self.name)
        if not reserved:
            return None

        message_id, message = reserved
        task_id, task = message_id, deserialize(message)
        return task_id, task

    def ack_task(self, task_id):
        message_id = task_id
        try:
            self._provider.ack(self.name, message_id)
        except MessageIDNotFound:
            raise TaskIDNotFound

    def get_pending_task_count(self):
        return self._provider.get_pending_message_count(self.name)

    def get_in_progress_task_count(self):
        return self._provider.get_in_progress_message_count(self.name)


def serialize(task: Task):
    return json.dumps({'task_name': task.name, 'task_payload': task.payload})


def deserialize(message):
    dikt = json.loads(message)
    return Task(name=dikt['task_name'], payload=dikt['task_payload'])
