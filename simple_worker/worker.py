class Worker:
    def __init__(self, queues, task_handler_registry, task_executor_cls):
        self._queues = queues
        self._task_executor_cls = task_executor_cls
        self._task_handler_registry = task_handler_registry
        self._shutdown_signal_received = False

    def register_on_boot_handler():
        pass

    def register_on_shutdown_handler():
        pass

    def register_on_task_start_handler():
        pass

    def register_on_task_end_handler():
        pass

    def register_on_task_failure_handler():
        pass

    def start(self):
        while not self._shutdown_signal_received:
            self._worker_loop()

    def _worker_loop(self):
        for queue in self.queues:
            reserved = queue.reserve_task()
            if not reserved:
                continue

        task_id, task = reserved

        task_handler_fn = self.task_handler_registry[task.name]
        self._task_executor_cls().execute(task.payload, task_handler_fn)

        queue.ack_task(task_id)

    def shutdown(self):
        self._shutdown_signal_received = True
