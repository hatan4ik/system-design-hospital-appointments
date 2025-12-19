import json
from datetime import datetime, timedelta
from . import crud, database
from .config import settings
import redis
from fastapi import HTTPException

r = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

def get_availability(provider_id: str, start: datetime, end: datetime, slot_minutes: int):
    if end <= start:
        raise HTTPException(status_code=400, detail="end must be after start")

    key = f"avail:{provider_id}:{start.isoformat()}:{end.isoformat()}:{slot_minutes}"
    cached = r.get(key)
    if cached:
        return json.loads(cached)

    with database.get_db_connection() as conn:
        with conn.cursor() as cur:
            schedules = crud.get_provider_schedules(cur, provider_id, start, end)
            busy = crud.get_appointments(cur, provider_id, start, end)

    shifts = [(max(s, start), min(e, end)) for s, e, k in schedules if k == "SHIFT"]
    if not shifts:
        resp = {"provider_id": provider_id, "from": start.isoformat(), "to": end.isoformat(), "slots": []}
        r.set(key, json.dumps(resp), ex=settings.AVAILABILITY_CACHE_TTL_SECONDS)
        return resp

    blocked = [(max(s, start), min(e, end)) for s, e, k in schedules if k != "SHIFT"]
    busy = busy + blocked
    slots = []
    t = start
    step = timedelta(minutes=slot_minutes)
    while t + step <= end:
        t2 = t + step
        within_shift = any(t >= s and t2 <= e for s, e in shifts)
        if within_shift and all(t2 <= bs or t >= be for bs, be in busy):
            slots.append({"start": t.isoformat(), "end": t2.isoformat()})
        t = t2

    resp = {"provider_id": provider_id, "from": start.isoformat(), "to": end.isoformat(), "slots": slots}
    r.set(key, json.dumps(resp), ex=settings.AVAILABILITY_CACHE_TTL_SECONDS)
    return resp
