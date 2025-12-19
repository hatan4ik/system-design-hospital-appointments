"""
Unit tests for the Availability service API.
"""
import json
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import fakeredis
import pytest
from fastapi.testclient import TestClient

from . import main, services, database

client = TestClient(main.app)

@pytest.fixture
def mock_redis():
    """
    Fixture to mock the Redis client.
    """
    r = fakeredis.FakeRedis(decode_responses=True)
    with patch.object(services, "r", r):
        yield r
    r.flushall()
    r.close()


@pytest.fixture
def mock_psycopg():
    """
    Fixture to mock the psycopg2 PostgreSQL database driver.
    """
    with patch.object(database, "psycopg") as mock_psycopg_module:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_psycopg_module.connect.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []
        yield mock_cursor


def test_healthz():
    """
    Test the /healthz endpoint.
    """
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_availability_end_before_start():
    """
    Test that a 400 error is returned when the end time is before the start time.
    """
    start = datetime(2025, 1, 1, 10, 0)
    end = datetime(2025, 1, 1, 9, 0)
    response = client.get(f"/availability?provider_id=p1&start={start.isoformat()}&end={end.isoformat()}")
    assert response.status_code == 400
    assert response.json() == {"detail": "end must be after start"}


def test_availability_cached(mock_redis):
    """
    Test that a cached response is returned if available.
    """
    provider_id = "p1"
    start = datetime(2025, 1, 1, 9, 0)
    end = datetime(2025, 1, 1, 17, 0)
    slot_minutes = 30
    key = f"avail:{provider_id}:{start.isoformat()}:{end.isoformat()}:{slot_minutes}"
    cached_data = {"provider_id": provider_id, "slots": []}
    mock_redis.set(key, json.dumps(cached_data))

    response = client.get(f"/availability?provider_id={provider_id}&start={start.isoformat()}&end={end.isoformat()}&slot_minutes={slot_minutes}")
    assert response.status_code == 200
    assert response.json() == cached_data

def test_no_shifts(mock_redis, mock_psycopg):
    """
    Test that an empty list of slots is returned when the provider has no shifts.
    """
    provider_id = "p1"
    start = datetime(2025, 1, 1, 9, 0)
    end = datetime(2025, 1, 1, 17, 0)
    
    mock_psycopg.fetchall.return_value = []

    response = client.get(f"/availability?provider_id={provider_id}&start={start.isoformat()}&end={end.isoformat()}")
    assert response.status_code == 200
    data = response.json()
    assert data["slots"] == []


@pytest.mark.parametrize("schedules, appointments, expected_slots", [
    (
        # One shift, no appointments
        [(datetime(2025, 1, 1, 9), datetime(2025, 1, 1, 12), "SHIFT")],
        [],
        [
            {"start": "2025-01-01T09:00:00", "end": "2025-01-01T09:15:00"},
            {"start": "2025-01-01T09:15:00", "end": "2025-01-01T09:30:00"},
        ]
    ),
    (
        # One shift, one appointment
        [(datetime(2025, 1, 1, 9), datetime(2025, 1, 1, 10), "SHIFT")],
        [(datetime(2025, 1, 1, 9, 15), datetime(2025, 1, 1, 9, 30))],
        [
            {"start": "2025-01-01T09:00:00", "end": "2025-01-01T09:15:00"},
        ]
    ),
    (
        # One shift, one break
        [(datetime(2025, 1, 1, 9), datetime(2025, 1, 1, 10), "SHIFT"), (datetime(2025, 1, 1, 9, 15), datetime(2025, 1, 1, 9, 30), "BREAK")],
        [],
        [
            {"start": "2025-01-01T09:00:00", "end": "2025-01-01T09:15:00"},
        ]
    )
])
def test_availability_logic(mock_redis, mock_psycopg, schedules, appointments, expected_slots):
    provider_id = "p1"
    start = datetime(2025, 1, 1, 9, 0)
    end = datetime(2025, 1, 1, 10, 0)
    slot_minutes = 15

    mock_psycopg.fetchall.side_effect = [schedules, appointments]
    
    response = client.get(f"/availability?provider_id={provider_id}&start={start.isoformat()}&end={end.isoformat()}&slot_minutes={slot_minutes}")
    
    assert response.status_code == 200
    data = response.json()
    
    # Check a subset of slots to keep the test concise
    for expected_slot in expected_slots:
        assert expected_slot in data["slots"]

