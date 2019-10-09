import os
from unittest.mock import patch, MagicMock

import pytest
import boto3
import random
import string

from botocore.exceptions import ClientError

from simple_worker.queue_providers import SQSProvider
from simple_worker.queue_providers.exceptions import (
    MessageIDNotFound,
    QueueNotFound,
    InvalidCredentials,
)

CREDS_FILE = os.path.join(os.getcwd(), "tests", ".aws_credentials")


@pytest.mark.integration
def test_add_and_reserve(provider):
    provider.add("dummy_queue", "msg1")
    provider.add("dummy_queue", "msg2")

    messages = []

    message_id, message = provider.reserve_one("dummy_queue")
    messages.append(message)

    message_id, message = provider.reserve_one("dummy_queue")
    messages.append(message)

    # SQS doesn't guarantee order, let's check after sorting
    assert sorted(messages) == sorted(["msg1", "msg2"])

    assert provider.reserve_one("dummy_queue") is None


@pytest.mark.integration
def test_queue_not_found_error(provider):
    with pytest.raises(MessageIDNotFound):
        provider.ack("dummy_queue", "invalid")


@patch("simple_worker.queue_providers.sqs_provider.boto3")
def test_retries_for_invalid_credentials(mock_boto):
    boto_client = MagicMock()
    boto_client.get_queue_url.side_effect = ClientError(
        error_response={"Error": {"Code": "InvalidClientTokenId"}},
        operation_name="get_queue",
    )
    mock_boto.client.return_value = boto_client
    sqs_provider = SQSProvider("simple_worker_tests_%s_" % random_str())
    with pytest.raises(InvalidCredentials):
        sqs_provider.add("test_queue", "test_message")

    assert boto_client.get_queue_url.call_count == 3


@pytest.mark.integration
def test_ack(provider):
    with pytest.raises(QueueNotFound):
        provider.ack("inexistent_queue", "invalid")


@pytest.fixture
def aws_creds():
    os.environ["AWS_SHARED_CREDENTIALS_FILE"] = CREDS_FILE
    os.environ["AWS_REGION"] = "dummy"

    yield

    del os.environ["AWS_SHARED_CREDENTIALS_FILE"]


@pytest.fixture
def provider(aws_creds):
    randomized_prefix = "simple_worker_tests_%s_" % random_str()
    queue_name = randomized_prefix + "dummy_queue"

    resp = boto3.client("sqs").create_queue(QueueName=queue_name)
    queue_url = resp["QueueUrl"]

    yield SQSProvider(queue_prefix=randomized_prefix)

    boto3.client("sqs").delete_queue(QueueUrl=queue_url)


def random_str():
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(10))
