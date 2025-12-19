"""
Unit tests for the Appointment service API.

This module contains tests for the FastAPI application in main.py.
It uses pytest fixtures to mock external dependencies like Redis and PostgreSQL,
allowing for isolated and predictable testing of the API endpoints.
"""
import json
from datetime import datetime
from unittest.mock import MagicMock, patch, AsyncMock

import fakeredis
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient

from . import main, services, database, schemas
from .services import req_hash

client = TestClient(main.app)

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
    r = fakeredis.FakeRedis(decode_responses=True)
    with patch.object(services, "r", r):
        yield r
    r.flushall()
    r.close()


@pytest_asyncio.fixture
async def mock_asyncpg():
    """
    Fixture to mock the asyncpg PostgreSQL database driver.
    """
    mock_conn = AsyncMock()
    mock_conn.transaction.return_value = AsyncMock()
    
    with patch.object(database, "asyncpg") as mock_asyncpg_module:
        mock_asyncpg_module.connect.return_value = mock_conn
        yield mock_conn


def test_healthz():
    """
    Test the /healthz endpoint.
    """
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"ok": True}


@pytest.mark.asyncio
async def test_book_missing_idempotency_key():
    """
    Test booking an appointment without an Idempotency-Key header.
    """
    req = schemas.BookRequest(
        patient_id="p1",
        provider_id="prov1",
        visit_type="vt1",
        start_ts=datetime(2025, 1, 1, 9, 0),
        end_ts=datetime(2025, 1, 1, 9, 30),
        location_id="loc1",
    )
    response = client.post("/appointments", json=req.model_dump(mode="json"))
    assert response.status_code == 400
    assert response.json() == {"detail": "Idempotency-Key required"}

@pytest.mark.asyncio
async def test_book_cached_response(mock_redis):
    """
    Test that a cached response is returned for a repeated Idempotency-Key.
    """
    req = schemas.BookRequest(
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

@pytest.mark.asyncio
async def test_book_busy_retry(mock_redis):
    """
    Test booking an appointment when a distributed lock is held.
    """
    req = schemas.BookRequest(
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

@pytest.mark.asyncio
async def test_book_time_conflict(mock_redis, mock_asyncpg):
    """
    Test booking an appointment that conflicts with an existing one.
    """
    req = schemas.BookRequest(
        patient_id="p1",
        provider_id="prov1",
        visit_type="vt1",
        start_ts=datetime(2025, 1, 1, 9, 0),
        end_ts=datetime(2025, 1, 1, 9, 30),
        location_id="loc1",
    )
    mock_asyncpg.fetchrow.side_effect = [
        None,  # idempotency lookup miss
        True,   # conflicting appointment exists
    ]
    mock_asyncpg.fetchval.return_value = True # advisory lock acquired

    response = client.post("/appointments", headers={"Idempotency-Key": "some-key"}, json=req.model_dump(mode="json"))

    assert response.status_code == 409
    assert response.json() == {"detail": "Time conflict"}


@pytest.mark.asyncio
async def test_book_successful(mock_redis, mock_asyncpg):
    """
    This is the "happy path" test case. 
    """
    req = schemas.BookRequest(
        patient_id="p1",
        provider_id="prov1",
        visit_type="vt1",
        start_ts=datetime(2025, 1, 1, 9, 0),
        end_ts=datetime(2025, 1, 1, 9, 30),
        location_id="loc1",
    )
    mock_asyncpg.fetchrow.side_effect = [
        None,      # idempotency miss
        None,      # no conflicting appointment
    ]
    mock_asyncpg.fetchval.return_value = True # advisory lock acquired

    response = client.post("/appointments", headers={"Idempotency-Key": "some-key"}, json=req.model_dump(mode="json"))

    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json["status"] == "CONFIRMED"
    assert resp_json["appointment_id"].startswith("apt_")

    assert mock_asyncpg.execute.call_count > 0


@pytest.mark.asyncio
async def test_idempotency_payload_mismatch(mock_redis, mock_asyncpg):
    """
    Reusing an Idempotency-Key with a different payload should be rejected.
    """
    req = schemas.BookRequest(
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
    mock_asyncpg.fetchrow.side_effect = [
        ("different-hash", json.dumps(cached_resp["response"])),
    ]
    response = client.post("/appointments", headers={"Idempotency-Key": "idem-key"}, json=req.model_dump(mode="json"))
    assert response.status_code == 400
    assert response.json() == {"detail": "Idempotency-Key has different payload"}

    cached_val = mock_redis.get("idem:idem-key")
    assert cached_val is None

@pytest.mark.asyncio
async def test_get_appointment_found(mock_asyncpg):
    """
    Test retrieving an existing appointment.
    """
    appointment_id = "apt_123"
    appointment_data = {
        "id": appointment_id,
        "patient_id": "p1",
        "provider_id": "prov1",
        "start_ts": datetime(2025, 1, 1, 9, 0),
        "end_ts": datetime(2025, 1, 1, 9, 15),
        "status": "CONFIRMED",
        "visit_type": "FOLLOW_UP_15",
        "location_id": "loc1",
    }
    mock_asyncpg.fetchrow.return_value = appointment_data

    response = client.get(f"/appointments/{appointment_id}")

    assert response.status_code == 200
    assert response.json()["id"] == appointment_id

@pytest.mark.asyncio
async def test_get_appointment_not_found(mock_asyncpg):
    """
    Test retrieving a non-existent appointment.
    """
    appointment_id = "apt_404"
    mock_asyncpg.fetchrow.return_value = None

    response = client.get(f"/appointments/{appointment_id}")

    assert response.status_code == 404
    assert response.json() == {"detail": "Appointment not found"}