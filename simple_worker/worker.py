import logging
import json
import traceback

logger = logging.getLogger('simple_worker')


class Worker:
    def __init__(self, queues, task_handler_registry, task_executor_cls):
        self._queues = queues
        self._task_executor_cls = task_executor_cls
        self._task_handler_registry = task_handler_registry
        self._shutdown_signal_received = False

    def start(self):
        while not self._shutdown_signal_received:
            self._worker_loop()

    def _worker_loop(self):
        reserved = self._reserve_one()
        if not reserved:
            return

        queue, task_id, task = reserved

        task_handler_fn = self._task_handler_registry.get(task.name)
        executor = self._task_executor_cls(task_handler_fn)
        is_success, exc = executor.execute(task)

        if is_success:
            # We only ack tasks if they were succesfully processed. Retrying
            # failed tasks is the responsibility of the queue - it ensures
            # that tasks that were received but not acked are resurfaced to
            # consumers.
            queue.ack_task(task_id)
        else:
            self._log_exc(task, task_id, exc)

    def _log_exc(task, task_id, exc):
        # TODO: Add attempt count?
        logger.error(
            "Task raised exception, will be retried by queue",
            extra={
                'exc': str(exc),
                'task_id': task_id,
                'task_name': task.name,
                'task_payload': json.dumps(task.payload)
            })

    def _reserve_one(self):
        for queue in self._queues:
            reserved = queue.reserve_task()
            if not reserved:
                continue

        if reserved:
            return (queue, *reserved)
        else:
            return None

    def shutdown(self):
        self._shutdown_signal_received = True
