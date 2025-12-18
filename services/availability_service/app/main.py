import os, json
from datetime import datetime, timedelta
import psycopg, redis
from fastapi import FastAPI, HTTPException, Query

DB_DSN = os.getenv("DB_DSN", "postgresql://postgres:postgres@db:5432/postgres")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

r = redis.Redis.from_url(REDIS_URL, decode_responses=True)
app = FastAPI(title="availability-service")

@app.get("/healthz")
def healthz():
    return {"ok": True}

@app.get("/availability")
def availability(provider_id: str, start: datetime, end: datetime, slot_minutes: int = Query(15, ge=5, le=120)):
    if end <= start:
        raise HTTPException(status_code=400, detail="end must be after start")

    key = f"avail:{provider_id}:{start.date().isoformat()}:{slot_minutes}"
    cached = r.get(key)
    if cached:
        return json.loads(cached)

    with psycopg.connect(DB_DSN) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT start_ts, end_ts FROM appointments
                WHERE provider_id = %s
                  AND status IN ('HELD','CONFIRMED')
                  AND start_ts < %s AND end_ts > %s
                ORDER BY start_ts
                """,
                (provider_id, end, start),
            )
            busy = cur.fetchall()

    slots = []
    t = start
    step = timedelta(minutes=slot_minutes)
    while t + step <= end:
        t2 = t + step
        if all(t2 <= bs or t >= be for bs, be in busy):
            slots.append({"start": t.isoformat(), "end": t2.isoformat()})
        t = t2

    resp = {"provider_id": provider_id, "from": start.isoformat(), "to": end.isoformat(), "slots": slots}
    r.set(key, json.dumps(resp), ex=60)
    return resp
