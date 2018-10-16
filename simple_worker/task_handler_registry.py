class TaskHandlerAlreadyRegistered(Exception):
    pass


class TaskHandlerNotFound(Exception):
    pass


class TaskHandlerRegistry():
    def __init__(self):
        self.data = {}

    def register(self, task_name, handler_fn):
        if task_name in self.data:
            raise TaskHandlerAlreadyRegistered(task_name)

        self.data[task_name] = handler_fn

    def get(self, task_name):
        if task_name not in self.data:
            raise TaskHandlerNotFound(task_name)

        return self.data[task_name]
