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
        Reserves a task from the queue.

        Returns a tuple of (task_id, task).

        task_id can be used to `ack` the task after processing
        """
        message_id, message = self._provider.reserve_one(self.name)
        task_id, task = message_id, deserialize(message)
        return task_id, task

    def ack_task(self, task_id):
        message_id = task_id
        self._provider.ack(self.name, message_id)

    def get_pending_task_count(self):
        pass

    def get_in_progress_task_count(self):
        pass


def serialize(task):
    return {'task_name': task.name, 'task_payload': task.payload}


def deserialize(message):
    return Task(name=message['task_name'], payload=message['task_payload'])
