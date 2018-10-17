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

    def has_handler_for(self, task_name):
        return task_name in self.data

    def get(self, task_name):
        if not self.has_handler_for(task_name):
            raise TaskHandlerNotFound(task_name)

        return self.data[task_name]
