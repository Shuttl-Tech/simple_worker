import os
import pytest
import boto3
import random
import string

from simple_worker.queue_providers import SQSProvider
from simple_worker.queue_providers.exceptions import MessageIDNotFound, QueueNotFound

CREDS_FILE = os.path.join(os.getcwd(), 'tests', '.aws_credentials')


@pytest.mark.integration
def test_add_and_reserve(provider):
    provider.add('dummy_queue', 'msg1')
    provider.add('dummy_queue', 'msg2')

    messages = []

    message_id, message = provider.reserve_one('dummy_queue')
    messages.append(message)

    message_id, message = provider.reserve_one('dummy_queue')
    messages.append(message)

    # SQS doesn't guarantee order, let's check after sorting
    assert sorted(messages) == sorted(['msg1', 'msg2'])

    assert provider.reserve_one('dummy_queue') is None


@pytest.mark.integration
def test_queue_not_found_error(provider):
    with pytest.raises(MessageIDNotFound):
        provider.ack('dummy_queue', 'invalid')


@pytest.mark.integration
def test_ack(provider):
    with pytest.raises(QueueNotFound):
        provider.ack('inexistent_queue', 'invalid')


@pytest.fixture
def aws_creds():
    os.environ["AWS_SHARED_CREDENTIALS_FILE"] = CREDS_FILE

    yield

    del os.environ["AWS_SHARED_CREDENTIALS_FILE"]


@pytest.fixture
def provider(aws_creds):
    randomized_prefix = 'simple_worker_tests_%s_' % random_str()
    queue_name = randomized_prefix + 'dummy_queue'

    resp = boto3.client('sqs').create_queue(QueueName=queue_name)
    queue_url = resp['QueueUrl']

    yield SQSProvider(queue_prefix=randomized_prefix)

    boto3.client('sqs').delete_queue(QueueUrl=queue_url)


def random_str():
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(10))
