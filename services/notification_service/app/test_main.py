"""
Unit tests for the Notification service API.
"""
import asyncio
import json
from unittest.mock import patch, MagicMock

import pytest
from fastapi.testclient import TestClient
import fakeredis.aioredis

from . import main

client = TestClient(main.app)

@pytest.fixture
def mock_redis():
    """
    Fixture to mock the Redis client.
    """
    r = fakeredis.aioredis.FakeRedis(decode_responses=True)
    with patch.object(main, "redis", r):
        yield r
    r.flushall()

def test_healthz():
    """
    Test the /healthz endpoint.
    """
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"ok": True}

@pytest.mark.asyncio
async def test_subscribe_to_appointments(mock_redis, capsys):
    """
    Test that the service subscribes to the 'appointments' channel and processes messages.
    """
    # Patch the print function to capture output
    with patch('builtins.print') as mock_print:
        # Start the subscription task
        task = asyncio.create_task(main.subscribe_to_appointments())
        await asyncio.sleep(0.1) # allow time for subscription to establish

        # Publish a message
        test_message = {"event": "appointment_created", "appointment_id": "apt_123"}
        await mock_redis.publish("appointments", json.dumps(test_message))
        await asyncio.sleep(0.1) # allow time for message to be processed

        # Check that the message was printed
        mock_print.assert_called_with(f"Received message: {json.dumps(test_message)}")

        # Clean up the task
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
