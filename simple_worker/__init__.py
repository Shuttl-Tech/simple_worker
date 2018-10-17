from simple_worker.task_handler_registry import TaskHandlerRegistry
from simple_worker.queue import Queue
from simple_worker.worker import Worker
from simple_worker.queue_providers import MemoryProvider, SQSProvider


class App:
    def __init__(self, broker_url):
        self._task_handler_registry = TaskHandlerRegistry()
        self._task_router = {}
        self._queue_provider = provider_from_broker_url(broker_url)

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
            self._task_router[task_name] = queue

        return f

    def add_task(self, task_name, **payload):
        """
        Usage:

        app.add_task('my_task', param1='a', param2='b')
        """
        queue_name = self._task_router[task_name]
        self.get_queue(queue_name).add_task(task_name, payload)

    def get_queue(self, queue_name):
        return Queue(self._queue_provider, queue_name)

    def process_tasks(self, queue_names=['default']):
        queues = [self.get_queue(queue_name) for queue_name in queue_names]
        Worker(queues).start()


def provider_from_broker_url(broker_url):
    if broker_url.startswith('memory://'):
        return MemoryProvider()
    else:
        raise RuntimeError("Invalid broker_url: " + broker_url)
