from contextlib import contextmanager
from typing import Tuple, Optional

TaskExecutionResult = Tuple[bool, Optional[Exception]]


class TaskExecutor():
    def __init__(self, task_handler_fn):
        self.task_handler_fn = task_handler_fn

    @contextmanager
    def context(self):
        """
        Override this in a subclass to execute a task within a specific context
        """
        yield

    def execute(self, task) -> TaskExecutionResult:
        try:
            with self.context():
                self.task_handler_fn(**task.payload)
        except Exception as e:
            return False, e

        return True, None
