import pytest

from simple_worker.queue_providers import MemoryProvider
from simple_worker.queue_providers import MessageIDNotFound


def test_add_and_reserve():
    provider = MemoryProvider()

    provider.add('dummy_queue', 'msg1')
    provider.add('dummy_queue', 'msg2')

    message_id, message = provider.reserve_one('dummy_queue')
    assert message == 'msg1'

    message_id, message = provider.reserve_one('dummy_queue')
    assert message == 'msg2'


def test_ack():
    provider = MemoryProvider()

    with pytest.raises(MessageIDNotFound):
        provider.ack('dummy_queue', 'invalid')

    provider.add('dummy_queue', 'msg1')
    provider.add('dummy_queue', 'msg2')

    message_id, message = provider.reserve_one('dummy_queue')
    provider.ack('dummy_queue', message_id)

    message_id, message = provider.reserve_one('dummy_queue')
    provider.ack('dummy_queue', message_id)
