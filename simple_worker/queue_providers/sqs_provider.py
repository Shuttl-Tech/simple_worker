from .exceptions import MessageIDNotFound


class SQSProvider():
    def __init__(self, sqs_url):
        pass

    def add(self, queue_name, message):
        pass

    def reserve_one(self, queue_name):
        pass

    def ack(self, queue_name, message_id):
        pass
