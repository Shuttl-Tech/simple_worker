class Worker:
    def __init__(self, queues, task_handler_registry, task_executor_cls):
        self._queues = queues
        self._task_executor_cls = task_executor_cls
        self._task_handler_registry = task_handler_registry
        self._shutdown_signal_received = False

    def register_on_boot_handler(self):
        pass

    def register_on_shutdown_handler(self):
        pass

    def register_on_task_start_handler(self):
        pass

    def register_on_task_end_handler(self):
        pass

    def register_on_task_failure_handler(self):
        pass

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

        if not is_success:
            # Log out the exception
            # Queue for retrial?
            pass
        else:
            queue.ack_task(task_id)

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
