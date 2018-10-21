from simple_worker.task_handler_registry import TaskHandlerRegistry
from simple_worker.task_handler_registry import TaskHandlerNotFound
from simple_worker.task_router import TaskRouter
from simple_worker.queue import Queue
from simple_worker.worker import Worker
from simple_worker.queue_providers import MemoryProvider, SQSProvider
from simple_worker.task import Task
from simple_worker.task_executor import TaskExecutor


class App:
    def __init__(self, queue_prefix: str = '', testing_mode: bool = False):
        self._task_handler_registry = TaskHandlerRegistry()
        self._task_router = TaskRouter()

        if testing_mode:
            self._queue_provider = MemoryProvider(queue_prefix=queue_prefix)
        else:
            self._queue_provider = SQSProvider(queue_prefix=queue_prefix)

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

    def worker(self, queue_names=None, task_executor_cls=None):
        if not queue_names:
            queue_names = set(self._task_router.get_all_queues())

        if task_executor_cls is None:
            task_executor_cls = TaskExecutor

        queues = [self._get_queue(queue_name) for queue_name in queue_names]
        return Worker(
            queues=queues,
            task_handler_registry=self._task_handler_registry,
            task_executor_cls=task_executor_cls)

    def _get_queue(self, queue_name):
        return Queue(self._queue_provider, queue_name)
