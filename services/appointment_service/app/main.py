import hashlib, json, os, uuid
from datetime import datetime
from typing import Optional

import psycopg
from psycopg import conninfo
import redis
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

DB_DSN = os.getenv("DB_DSN", "postgresql://postgres:postgres@db:5432/postgres")
DB_SSLMODE = os.getenv("DB_SSLMODE", "prefer")
DB_CONNECT_TIMEOUT = int(os.getenv("DB_CONNECT_TIMEOUT", "10"))
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
REDIS_LOCK_TTL_SECONDS = int(os.getenv("REDIS_LOCK_TTL_SECONDS", "30"))
IDEMPOTENCY_CACHE_TTL_SECONDS = int(os.getenv("IDEMPOTENCY_CACHE_TTL_SECONDS", "3600"))
DB_CONNINFO = conninfo.make_conninfo(DB_DSN, sslmode=DB_SSLMODE, connect_timeout=DB_CONNECT_TIMEOUT)

r = redis.Redis.from_url(REDIS_URL, decode_responses=True)
app = FastAPI(title="appointment-service")

class BookRequest(BaseModel):
    patient_id: str
    provider_id: str
    visit_type: str
    start_ts: datetime
    end_ts: datetime
    location_id: str

class BookResponse(BaseModel):
    appointment_id: str
    status: str

def req_hash(req: BookRequest) -> str:
    s = json.dumps(req.model_dump(mode="json"), sort_keys=True).encode()
    return hashlib.sha256(s).hexdigest()

def provider_day_lock_keys(req: BookRequest) -> tuple[str, int]:
    """
    Returns the Redis lock key and a stable Postgres advisory lock key for a provider-day.
    Advisory lock uses 64-bit int derived from provider_id + day to serialize bookings per provider/day.
    """
    day = req.start_ts.date().isoformat()
    redis_key = f"lock:{req.provider_id}:{day}"
    lock_bytes = hashlib.sha256(f"{req.provider_id}:{day}".encode()).digest()[:8]
    advisory_key = int.from_bytes(lock_bytes, byteorder="big", signed=False)
    return redis_key, advisory_key

@app.get("/healthz")
def healthz():
    return {"ok": True}

@app.post("/appointments", response_model=BookResponse)
def book(req: BookRequest, idempotency_key: Optional[str] = Header(default=None, alias="Idempotency-Key")):
    if not idempotency_key:
        raise HTTPException(status_code=400, detail="Idempotency-Key required")

    idem = f"idem:{idempotency_key}"
    request_hash = req_hash(req)
    cached = r.get(idem)
    if cached:
        cached_obj = json.loads(cached)
        if cached_obj.get("request_hash") != request_hash:
            raise HTTPException(status_code=400, detail="Idempotency-Key has different payload")
        return BookResponse(**cached_obj["response"])

    lock_key, advisory_key = provider_day_lock_keys(req)
    if not r.set(lock_key, "1", nx=True, ex=REDIS_LOCK_TTL_SECONDS):
        raise HTTPException(status_code=409, detail="Busy, retry")

    try:
        with psycopg.connect(conninfo=DB_CONNINFO) as conn:
            with conn.cursor() as cur:
                # Check durable idempotency record
                cur.execute(
                    "SELECT request_hash, response_ref FROM idempotency_keys WHERE idempotency_key = %s",
                    (idempotency_key,),
                )
                idem_row = cur.fetchone()
                if idem_row:
                    existing_hash, response_ref = idem_row
                    if existing_hash != request_hash:
                        raise HTTPException(status_code=400, detail="Idempotency-Key has different payload")
                    response_payload = json.loads(response_ref)
                    r.set(idem, json.dumps({"request_hash": existing_hash, "response": response_payload}), ex=IDEMPOTENCY_CACHE_TTL_SECONDS)
                    return BookResponse(**response_payload)

                # Acquire per-provider/day advisory lock to serialize bookings even if Redis expires
                cur.execute("SELECT pg_try_advisory_xact_lock(%s)", (advisory_key,))
                locked = cur.fetchone()[0]
                if not locked:
                    raise HTTPException(status_code=409, detail="Busy, retry")

                cur.execute(
                    """
                    SELECT 1 FROM appointments
                    WHERE provider_id = %s
                      AND status IN ('HELD','CONFIRMED')
                      AND NOT (end_ts <= %s OR start_ts >= %s)
                    LIMIT 1
                    """,
                    (req.provider_id, req.start_ts, req.end_ts),
                )
                if cur.fetchone():
                    cur.execute("ROLLBACK;")
                    raise HTTPException(status_code=409, detail="Time conflict")

                apt_id = f"apt_{uuid.uuid4().hex[:12]}"
                cur.execute(
                    """
                    INSERT INTO appointments(id, patient_id, provider_id, start_ts, end_ts, status, visit_type, location_id)
                    VALUES (%s,%s,%s,%s,%s,'CONFIRMED',%s,%s)
                    """,
                    (apt_id, req.patient_id, req.provider_id, req.start_ts, req.end_ts, req.visit_type, req.location_id),
                )
                cur.execute(
                    """
                    INSERT INTO appointment_audit(appointment_id, actor_id, action, payload)
                    VALUES (%s,%s,'APPOINTMENT_CREATED',%s::jsonb)
                    """,
                    (apt_id, req.patient_id, json.dumps(req.model_dump(mode="json"))),
                )
                cur.execute(
                    """
                    INSERT INTO idempotency_keys(idempotency_key, user_id, request_hash, response_ref)
                    VALUES (%s,%s,%s,%s)
                    """,
                    (idempotency_key, req.patient_id, request_hash, json.dumps({"appointment_id": apt_id, "status": "CONFIRMED"})),
                )

        resp = {"appointment_id": apt_id, "status": "CONFIRMED"}
        r.set(idem, json.dumps({"request_hash": request_hash, "response": resp}), ex=IDEMPOTENCY_CACHE_TTL_SECONDS)
        return BookResponse(**resp)
    finally:
        r.delete(lock_key)
