class TaskRouter:
    def __init__(self):
        self.task_to_queues = {}

    def add(self, task_name, queue_name):
        self.task_to_queues[task_name] = queue_name

    def get_queue_for_task(self, task_name):
        return self.task_to_queues[task_name]

    def get_all_queues(self):
        return set(self.task_to_queues.values())
