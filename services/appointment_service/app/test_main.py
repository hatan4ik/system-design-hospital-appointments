"""
Unit tests for the Appointment service API.

This module contains tests for the FastAPI application in main.py.
It uses pytest fixtures to mock external dependencies like Redis and PostgreSQL,
allowing for isolated and predictable testing of the API endpoints.
"""
import json
from datetime import datetime
from unittest.mock import MagicMock, patch

import fakeredis
import pytest
from fastapi.testclient import TestClient

from .main import BookRequest, app, req_hash

client = TestClient(app)

@pytest.fixture
def mock_redis():
    """
    Fixture to mock the Redis client.

    This fixture patches the Redis client used in the main application with an
    in-memory Redis implementation (fakeredis). This ensures that tests
    do not depend on a running Redis instance and that the Redis commands
    can be inspected.

    Yields:
        fakeredis.FakeRedis: An instance of the fake Redis client.
    """
    # Use fakeredis for in-memory redis
    server = fakeredis.FakeServer()
    r = fakeredis.FakeRedis(server=server, decode_responses=True)
    with patch("main.r", r):
        yield r
    r.close()
    server.close()


@pytest.fixture
def mock_psycopg():
    """
    Fixture to mock the psycopg2 PostgreSQL database driver.

    This fixture patches the psycopg2 module to avoid actual database connections
    during tests. It provides a mock cursor that can be used to control the
    return values of database queries, allowing for the simulation of different
    database states (e.g., finding or not finding conflicting appointments).

    Yields:
        MagicMock: A mock object representing the database cursor.
    """
    with patch("main.psycopg") as mock_psycopg_module:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_psycopg_module.connect.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        yield mock_cursor


def test_healthz():
    """
    Test the /healthz endpoint.

    This test ensures that the health check endpoint is functioning correctly,
    which is crucial for monitoring and service discovery in a production
    environment. It should return a 200 OK status and a specific JSON payload.
    """
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_book_missing_idempotency_key():
    """
    Test booking an appointment without an Idempotency-Key header.

    The API requires an Idempotency-Key for POST requests to ensure that
    duplicate requests are not processed multiple times. This test verifies
    that the server correctly rejects requests missing this header with a
    400 Bad Request error.
    """
    response = client.post("/appointments", json={})
    assert response.status_code == 400
    assert response.json() == {"detail": "Idempotency-Key required"}

def test_book_cached_response(mock_redis):
    """
    Test that a cached response is returned for a repeated Idempotency-Key.

    When a request with the same Idempotency-Key is received, the service
    should return the cached response from the first successful request.
    This test ensures that the idempotency logic is working correctly by
    pre-populating the cache and verifying that the cached response is returned.
    """
    req = BookRequest(
        patient_id="p1",
        provider_id="prov1",
        visit_type="vt1",
        start_ts=datetime(2025, 1, 1, 9, 0),
        end_ts=datetime(2025, 1, 1, 9, 30),
        location_id="loc1",
    )
    idem_key = "idem-key-1"
    cached_resp = {"appointment_id": "apt_cached", "status": "CONFIRMED"}
    mock_redis.set(f"idem:{idem_key}", json.dumps({"request_hash": req_hash(req), "response": cached_resp}))

    response = client.post("/appointments", headers={"Idempotency-Key": idem_key}, json=req.model_dump(mode="json"))
    
    assert response.status_code == 200
    assert response.json() == cached_resp

def test_book_busy_retry(mock_redis):
    """
    Test booking an appointment when a distributed lock is held.

    To prevent race conditions when booking appointments for the same provider
    on the same day, a distributed lock is used. This test simulates a scenario
    where the lock is already held, and verifies that the service returns a
    409 Conflict with a 'Busy, retry' message.
    """
    req = BookRequest(
        patient_id="p1",
        provider_id="prov1",
        visit_type="vt1",
        start_ts=datetime(2025, 1, 1, 9, 0),
        end_ts=datetime(2025, 1, 1, 9, 30),
        location_id="loc1",
    )
    day = req.start_ts.date().isoformat()
    lock_key = f"lock:{req.provider_id}:{day}"
    mock_redis.set(lock_key, "1")

    response = client.post("/appointments", headers={"Idempotency-Key": "some-key"}, json=req.model_dump(mode="json"))
    
    assert response.status_code == 409
    assert response.json() == {"detail": "Busy, retry"}

def test_book_time_conflict(mock_redis, mock_psycopg):
    """
    Test booking an appointment that conflicts with an existing one.

    This test checks the core logic for preventing double-booking. It uses the
    mock_psycopg fixture to simulate a database query that finds an existing,
    overlapping appointment. The test verifies that the service returns a 409
    Conflict with a 'Time conflict' message and that the database transaction
    is rolled back.
    """
    req = BookRequest(
        patient_id="p1",
        provider_id="prov1",
        visit_type="vt1",
        start_ts=datetime(2025, 1, 1, 9, 0),
        end_ts=datetime(2025, 1, 1, 9, 30),
        location_id="loc1",
    )
    # idempotency miss, lock acquired, then existing appointment found
    mock_psycopg.fetchone.side_effect = [
        None,          # idempotency lookup miss
        (True,),       # advisory lock acquired
        (1,),          # conflicting appointment exists
    ]

    response = client.post("/appointments", headers={"Idempotency-Key": "some-key"}, json=req.model_dump(mode="json"))

    assert response.status_code == 409
    assert response.json() == {"detail": "Time conflict"}


def test_book_successful(mock_redis, mock_psycopg):
    """
    Test the successful booking of a new appointment.

    This is the "happy path" test case. It verifies that when there are no
    conflicts or locks, a new appointment can be successfully created.
    The test ensures that:
    - The API returns a 200 OK status.
    - The response contains a 'CONFIRMED' status and an appointment ID.
    - A COMMIT is issued to the database.
    - The successful response is cached for idempotency.
    """
    req = BookRequest(
        patient_id="p1",
        provider_id="prov1",
        visit_type="vt1",
        start_ts=datetime(2025, 1, 1, 9, 0),
        end_ts=datetime(2025, 1, 1, 9, 30),
        location_id="loc1",
    )
    mock_psycopg.fetchone.side_effect = [
        None,      # idempotency miss
        (True,),   # advisory lock acquired
        None,      # no conflicting appointment
    ]

    response = client.post("/appointments", headers={"Idempotency-Key": "some-key"}, json=req.model_dump(mode="json"))

    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json["status"] == "CONFIRMED"
    assert resp_json["appointment_id"].startswith("apt_")

    # Ensure inserts were attempted
    executed_statements = [call[0][0].strip().split()[0] for call in mock_psycopg.execute.call_args_list]
    assert "INSERT" in executed_statements


def test_idempotency_payload_mismatch(mock_redis, mock_psycopg):
    """
    Reusing an Idempotency-Key with a different payload should be rejected.
    This covers both Redis cache and durable database checks.
    """
    req = BookRequest(
        patient_id="p1",
        provider_id="prov1",
        visit_type="vt1",
        start_ts=datetime(2025, 1, 1, 9, 0),
        end_ts=datetime(2025, 1, 1, 9, 30),
        location_id="loc1",
    )
    cached_resp = {"request_hash": "other-hash", "response": {"appointment_id": "apt_123", "status": "CONFIRMED"}}
    mock_redis.set("idem:idem-key", json.dumps(cached_resp))

    response = client.post("/appointments", headers={"Idempotency-Key": "idem-key"}, json=req.model_dump(mode="json"))
    assert response.status_code == 400
    assert response.json() == {"detail": "Idempotency-Key has different payload"}

    # Redis miss but DB hit with mismatched hash
    mock_redis.flushall()
    mock_psycopg.fetchone.side_effect = [
        ("different-hash", json.dumps(cached_resp["response"])),  # idempotency row with different hash
    ]
    response = client.post("/appointments", headers={"Idempotency-Key": "idem-key"}, json=req.model_dump(mode="json"))
    assert response.status_code == 400
    assert response.json() == {"detail": "Idempotency-Key has different payload"}

    # Check that the response was cached
    cached_val = mock_redis.get("idem:some-key")
    assert cached_val is not None
    assert json.loads(cached_val) == resp_json
