class TaskExecutor():
    def execute(payload, task_handler_fn):
        task_handler_fn(**payload)
