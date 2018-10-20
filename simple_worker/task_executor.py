from typing import Tuple, Optional

TaskExecutionResult = Tuple[bool, Optional[Exception]]


class TaskExecutor():
    def __init__(self, task_handler_fn):
        self.task_handler_fn = task_handler_fn

    def execute(self, task) -> TaskExecutionResult:
        self.task_handler_fn(**task.payload)
        try:
            pass
        except Exception as e:
            return False, e

        return True, None
