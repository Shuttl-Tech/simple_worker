import boto3

from .exceptions import MessageIDNotFound

from botocore.exceptions import ClientError


class SQSProvider():
    def __init__(self, queue_prefix):
        self.queue_prefix = queue_prefix
        self.client = boto3.client('sqs')

    def add(self, queue_name: str, message: str):
        self.client.send_message(
            QueueUrl=self._get_queue_url(queue_name), MessageBody=message)

    def reserve_one(self, queue_name):
        resp = self.client.receive_message(
            QueueUrl=self._get_queue_url(queue_name))

        if not resp['Messages']:
            return None
        else:
            assert len(resp['Messages']) == 1

            message = resp['Messages'][0]
            return message['ReceiptHandle'], message['Body']

    def ack(self, queue_name, message_id):
        try:
            self.client.delete_message(
                QueueUrl=self._get_queue_url(queue_name),
                ReceiptHandle=message_id)
        except ClientError as e:
            if e.response['Error']['Code'] == 'ReceiptHandleIsInvalid':
                raise MessageIDNotFound(message_id)
            else:
                raise e

    def _get_queue_url(self, queue_name):
        full_queue_name = self.queue_prefix + queue_name
        resp = self.client.get_queue_url(QueueName=full_queue_name)
        return resp['QueueUrl']
