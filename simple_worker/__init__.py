# Expose:
#   - add_task
#   - register_task_handler
#   - process_pending_tasks

from simple_worker.task_handler_registry import TaskHandlerRegistry
from simple_worker.queue import Queue
from simple_worker.worker import Worker

_task_handler_registry = TaskHandlerRegistry()


def register_task_handler(task_name, queue='default'):
    """
    Usage:

    @register_task_handler('my_task')
    def my_task(param1, param2):
        # Do something worthwhile
        pass
    """

    def f(handler_fn):
        _task_handler_registry.register(task_name, handler_fn)
        # _task_router.add(task_name, queue)

    return f


def get_queue(config, name):
    pass


def process_tasks(config, queue_names=['default']):
    Worker(queue_names).start()
