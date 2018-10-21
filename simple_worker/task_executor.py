from contextlib import contextmanager
import logging

import json

logger = logging.getLogger(__name__)


class TaskExecutor():
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
            self._log_start(task)
            with self.context():
                self.task_handler_fn(**task.payload)
        except Exception as exc:
            self._log_exception(task, exc)
            return False

        self._log_success(task)
        return True

    def _log_start(self, task):
        logger.info("Processing task", extra={'task_name': task.name})

    def _log_success(self, task):
        logger.info(
            "Processed task successfully", extra={'task_name': task.name})

    def _log_exception(self, task, exc):
        logger.error(
            "Failed to process task",
            extra={
                'exc': str(exc),
                'task_name': task.name,
                'task_payload': json.dumps(task.payload)
            })
