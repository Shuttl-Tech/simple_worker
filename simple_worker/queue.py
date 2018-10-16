class Queue:
    def __init__(self, name, backend):
        self._backend = backend
        self.name = name

    def add_task(self, task):
        """
        Adds a task to the queue
        """
        message = serialize(task)
        self._backend.add(message)

    def reserve_task(self):
        """
        Reserves a task from the queue.

        Returns a tuple of (task_id, task).

        task_id can be used to `ack` the task after processing
        """
        message_id, message = self._backend.reserve()
        task_id, task = message_id, deserialize(message)
        return task_id, task

    def ack_task(self, task_id):
        message_id = task_id
        self._backend.ack(message_id)

    def get_pending_task_count(self):
        pass

    def get_in_progress_task_count(self):
        pass
