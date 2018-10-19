from uuid import uuid4
from collections import deque


class SQSProvider():
    def __init__(self, sqs_url):
        pass

    def add(self, queue_name, message):
        pass

    def reserve_one(self, queue_name):
        pass

    def ack(self, queue_name, message_id):
        pass


class MessageIDNotFound(Exception):
    pass


class MemoryProvider():
    def __init__(self):
        self._mem_queues = {}

    def add(self, queue_name: str, message: str):
        pending, _reserved = self._get_or_create_queues(queue_name)
        message_id = uuid4()
        pending.append({'id': message_id, 'message': message})

    def reserve_one(self, queue_name: str) -> (str, str):
        pending, reserved = self._get_or_create_queues(queue_name)
        if not pending:
            return None

        message_dict = pending.popleft()
        message_id, message = message_dict['id'], message_dict['message']
        reserved[message_id] = message

        return message_id, message

    def ack(self, queue_name: str, message_id: str):
        pending, reserved = self._get_or_create_queues(queue_name)
        if message_id not in reserved:
            raise MessageIDNotFound(message_id)

        del reserved[message_id]

    def _get_or_create_queues(self, queue_name):
        if queue_name not in self._mem_queues:
            pending, reserved = deque(), {}
            self._mem_queues[queue_name] = (pending, reserved)

        return self._mem_queues[queue_name]
