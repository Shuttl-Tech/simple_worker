import boto3
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

from .exceptions import MessageIDNotFound, QueueNotFound, InvalidCredentials

from botocore.exceptions import ClientError


class SQSProvider:
    def __init__(self, queue_prefix, endpoint_url=None, aws_region=None):
        self.queue_prefix = queue_prefix
        self.client = boto3.client(
            "sqs", endpoint_url=endpoint_url, region_name=aws_region
        )

    def add(self, queue_name: str, message: str):
        self.client.send_message(
            QueueUrl=self._get_queue_url(queue_name), MessageBody=message
        )

    def reserve_one(self, queue_name):
        resp = self.client.receive_message(QueueUrl=self._get_queue_url(queue_name))

        if "Messages" not in resp:
            return None
        else:
            assert len(resp["Messages"]) == 1

            message = resp["Messages"][0]
            return message["ReceiptHandle"], message["Body"]

    def ack(self, queue_name, message_id):
        try:
            self.client.delete_message(
                QueueUrl=self._get_queue_url(queue_name), ReceiptHandle=message_id
            )
        except ClientError as e:
            if e.response["Error"]["Code"] == "ReceiptHandleIsInvalid":
                raise MessageIDNotFound(message_id)
            else:
                raise e

    # retrying coz aws credentials take a while to propagate in all regions:
    # https://docs.aws.amazon.com/IAM/latest/UserGuide/troubleshoot_general.html#troubleshoot_general_eventual-consistency
    @retry(
        retry=retry_if_exception_type(InvalidCredentials),
        stop=stop_after_attempt(3),
        wait=wait_fixed(1),
        reraise=True,
    )
    def _get_queue_url(self, queue_name):
        full_queue_name = self.queue_prefix + queue_name
        try:
            resp = self.client.get_queue_url(QueueName=full_queue_name)
        except ClientError as e:
            if e.response["Error"]["Code"] == "AWS.SimpleQueueService.NonExistentQueue":
                raise QueueNotFound(full_queue_name)
            elif e.response["Error"]["Code"] == "InvalidClientTokenId":
                raise InvalidCredentials(f"Invalid credentials for queue {queue_name}")
            else:
                raise e

        return resp["QueueUrl"]
