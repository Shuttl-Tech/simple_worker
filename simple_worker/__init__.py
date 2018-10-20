from simple_worker.task_handler_registry import TaskHandlerRegistry
from simple_worker.task_handler_registry import TaskHandlerNotFound
from simple_worker.task_router import TaskRouter
from simple_worker.queue import Queue
from simple_worker.worker import Worker
from simple_worker.queue_providers import MemoryProvider, SQSProvider
from simple_worker.task import Task


class App:
    def __init__(self, broker_url: str, queue_prefix: str = ''):
        self._task_handler_registry = TaskHandlerRegistry()
        self._task_router = TaskRouter()
        self._queue_provider = _get_provider(broker_url, queue_prefix)

    def register_task_handler(self, task_name, queue='default'):
        """
        Usage:

        @register_task_handler('my_task')
        def my_task(param1, param2):
            # Do something worthwhile
            pass
        """

        def f(handler_fn):
            self._task_handler_registry.register(task_name, handler_fn)
            self._task_router.add(task_name=task_name, queue_name=queue)

        return f

    def add_task(self, task_name, **payload):
        """
        Usage:

        app.add_task('my_task', param1='a', param2='b')
        """
        if not self._task_handler_registry.has_handler_for(task_name):
            raise TaskHandlerNotFound(task_name)

        task = Task(name=task_name, payload=payload)

        queue_name = self._task_router.get_queue_for_task(task_name)
        self._get_queue(queue_name).add_task(task)

    def process_tasks(self,
                      queue_names=None,
                      task_executor_cls=None,
                      max_tasks=None):
        if not queue_names:
            queue_names = set(self._task_router.values())

        queues = [self._get_queue(queue_name) for queue_name in queue_names]
        worker = Worker(
            queues=queues,
            task_handler_registry=self._task_handler_registry,
            task_executor_cls=task_executor_cls)
        worker.start()

    def _get_queue(self, queue_name):
        return Queue(self._queue_provider, queue_name)


def _get_provider(broker_url, queue_prefix):
    if broker_url.startswith('memory://'):
        return MemoryProvider(queue_prefix=queue_prefix)
    elif broker_url.startswith('sqs://'):
        return SQSProvider(queue_prefix=queue_prefix)
    else:
        raise ValueError("Invalid broker_url: " + broker_url)
