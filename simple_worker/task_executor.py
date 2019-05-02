from contextlib import contextmanager
import logging

import json

logger = logging.getLogger(__name__)


class TaskExecutor:
    def __init__(self, task_handler_fn):
        self.task_handler_fn = task_handler_fn

    @contextmanager
    def context(self):
        """
        Override this in a subclass to execute a task within a specific context
        """
        yield

    def execute(self, task) -> bool:
        try:
            self.log_start(task)
            with self.context():
                self.task_handler_fn(**task.payload)
        except Exception as exc:
            self.failure_handler(task, exc)
            return False
        else:
            self.success_handler(task)
            return True

    def log_start(self, task):
        """
        Override this in a subclass to perform action before starting a task
        """
        logger.info("Processing task", extra={"task_name": task.name})

    def failure_handler(self, task, exc):
        """
        Override this in a subclass to change failure handling
        Default: Logs Failure message with stacktrace and task info
        """
        logger.error(
            "Failed to process task",
            extra={
                "exc": str(exc),
                "task_name": task.name,
                "task_payload": json.dumps(task.payload),
            },
            exc_info=True,
        )

    def success_handler(self, task):
        """
        Override this in a subclass to change success handling.
        Default: Logs success message with task name
        """
        logger.info("Processed task successfully", extra={"task_name": task.name})
