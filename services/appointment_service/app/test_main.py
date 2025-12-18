import json
from datetime import datetime
from unittest.mock import MagicMock, patch

import fakeredis
import pytest
from fastapi.testclient import TestClient

from .main import BookRequest, app

client = TestClient(app)

@pytest.fixture
def mock_redis():
    # Use fakeredis for in-memory redis
    server = fakeredis.FakeServer()
    r = fakeredis.FakeRedis(server=server, decode_responses=True)
    with patch("main.r", r):
        yield r
    r.close()
    server.close()


@pytest.fixture
def mock_psycopg():
    with patch("main.psycopg") as mock_psycopg_module:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_psycopg_module.connect.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        yield mock_cursor


def test_healthz():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_book_missing_idempotency_key():
    response = client.post("/appointments", json={})
    assert response.status_code == 400
    assert response.json() == {"detail": "Idempotency-Key required"}

def test_book_cached_response(mock_redis):
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
    mock_redis.set(f"idem:{idem_key}", json.dumps(cached_resp))

    response = client.post("/appointments", headers={"Idempotency-Key": idem_key}, json=req.model_dump(mode="json"))
    
    assert response.status_code == 200
    assert response.json() == cached_resp

def test_book_busy_retry(mock_redis):
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
    req = BookRequest(
        patient_id="p1",
        provider_id="prov1",
        visit_type="vt1",
        start_ts=datetime(2025, 1, 1, 9, 0),
        end_ts=datetime(2025, 1, 1, 9, 30),
        location_id="loc1",
    )
    # Simulate an existing appointment
    mock_psycopg.fetchone.return_value = (1,)

    response = client.post("/appointments", headers={"Idempotency-Key": "some-key"}, json=req.model_dump(mode="json"))

    assert response.status_code == 409
    assert response.json() == {"detail": "Time conflict"}
    mock_psycopg.execute.assert_any_call("ROLLBACK;")


def test_book_successful(mock_redis, mock_psycopg):
    req = BookRequest(
        patient_id="p1",
        provider_id="prov1",
        visit_type="vt1",
        start_ts=datetime(2025, 1, 1, 9, 0),
        end_ts=datetime(2025, 1, 1, 9, 30),
        location_id="loc1",
    )
    # Simulate no existing appointment
    mock_psycopg.fetchone.return_value = None

    response = client.post("/appointments", headers={"Idempotency-Key": "some-key"}, json=req.model_dump(mode="json"))

    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json["status"] == "CONFIRMED"
    assert resp_json["appointment_id"].startswith("apt_")

    # Check that the appointment was inserted
    mock_psycopg.execute.assert_any_call("COMMIT;")

    # Check that the response was cached
    cached_val = mock_redis.get("idem:some-key")
    assert cached_val is not None
    assert json.loads(cached_val) == resp_json
