import json
import pytest
from sentinel.queue.redis_queue import RedisQueue


@pytest.fixture
def queue():
    q = RedisQueue(queue_name="test_queue")
    yield q
    q.flush()


def test_enqueue_dequeue(queue):
    item = {"service_name": "test", "message": "hello"}
    queue.enqueue(item)
    result = queue.dequeue(timeout=1)
    assert result == item


def test_dequeue_empty(queue):
    result = queue.dequeue(timeout=1)
    assert result is None
