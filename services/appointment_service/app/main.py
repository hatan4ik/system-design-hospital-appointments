import hashlib, json, os, uuid
from datetime import datetime
from typing import Optional

import psycopg
import redis
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

DB_DSN = os.getenv("DB_DSN", "postgresql://postgres:postgres@db:5432/postgres")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

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

@app.get("/healthz")
def healthz():
    return {"ok": True}

@app.post("/appointments", response_model=BookResponse)
def book(req: BookRequest, idempotency_key: Optional[str] = Header(default=None, alias="Idempotency-Key")):
    if not idempotency_key:
        raise HTTPException(status_code=400, detail="Idempotency-Key required")

    idem = f"idem:{idempotency_key}"
    cached = r.get(idem)
    if cached:
        return BookResponse(**json.loads(cached))

    # lock scope: provider + day
    day = req.start_ts.date().isoformat()
    lock_key = f"lock:{req.provider_id}:{day}"
    if not r.set(lock_key, "1", nx=True, ex=5):
        raise HTTPException(status_code=409, detail="Busy, retry")

    try:
        with psycopg.connect(DB_DSN) as conn:
            with conn.cursor() as cur:
                cur.execute("BEGIN;")
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
                cur.execute("COMMIT;")

        resp = {"appointment_id": apt_id, "status": "CONFIRMED"}
        r.set(idem, json.dumps(resp), ex=3600)
        return BookResponse(**resp)
    finally:
        r.delete(lock_key)
