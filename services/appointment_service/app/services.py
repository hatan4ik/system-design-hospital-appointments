import hashlib
import json
from . import crud, schemas, database
from .config import settings
import redis
from fastapi import HTTPException

r = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

def req_hash(req: schemas.BookRequest) -> str:
    s = json.dumps(req.model_dump(mode="json"), sort_keys=True).encode()
    return hashlib.sha256(s).hexdigest()

def provider_day_lock_keys(req: schemas.BookRequest) -> tuple[str, int]:
    day = req.start_ts.date().isoformat()
    redis_key = f"lock:{req.provider_id}:{day}"
    lock_bytes = hashlib.sha256(f"{req.provider_id}:{day}".encode()).digest()[:8]
    advisory_key = int.from_bytes(lock_bytes, byteorder="big", signed=False)
    return redis_key, advisory_key

async def book_appointment(req: schemas.BookRequest, idempotency_key: str):
    request_hash = req_hash(req)
    idem = f"idem:{idempotency_key}"
    
    cached = r.get(idem)
    if cached:
        cached_obj = json.loads(cached)
        if cached_obj.get("request_hash") != request_hash:
            raise HTTPException(status_code=400, detail="Idempotency-Key has different payload")
        return schemas.BookResponse(**cached_obj["response"])

    lock_key, advisory_key = provider_day_lock_keys(req)
    if not r.set(lock_key, "1", nx=True, ex=settings.REDIS_LOCK_TTL_SECONDS):
        raise HTTPException(status_code=409, detail="Busy, retry")

    try:
        conn = await database.get_db_connection()
        try:
            async with conn.transaction():
                idem_row = await crud.get_idempotency_key(conn, idempotency_key)
                if idem_row:
                    existing_hash, response_ref = idem_row
                    if existing_hash != request_hash:
                        raise HTTPException(status_code=400, detail="Idempotency-Key has different payload")
                    response_payload = json.loads(response_ref)
                    r.set(idem, json.dumps({"request_hash": existing_hash, "response": response_payload}), ex=settings.IDEMPOTENCY_CACHE_TTL_SECONDS)
                    return schemas.BookResponse(**response_payload)

                locked = await conn.fetchval("SELECT pg_try_advisory_xact_lock($1)", advisory_key)
                if not locked:
                    raise HTTPException(status_code=409, detail="Busy, retry")

                if await crud.check_appointment_conflict(conn, req.provider_id, req.start_ts, req.end_ts):
                    raise HTTPException(status_code=409, detail="Time conflict")

                apt_id = await crud.create_appointment(conn, req)
                await crud.create_appointment_audit(conn, apt_id, req.patient_id, req)
                
                resp = {"appointment_id": apt_id, "status": "CONFIRMED"}
                await crud.create_idempotency_key(conn, idempotency_key, req.patient_id, request_hash, resp)
        finally:
            await conn.close()
        
        r.set(idem, json.dumps({"request_hash": request_hash, "response": resp}), ex=settings.IDEMPOTENCY_CACHE_TTL_SECONDS)
        
        # Publish event
        event_payload = {"event": "appointment_created", "appointment_id": apt_id, "patient_id": req.patient_id}
        r.publish("appointments", json.dumps(event_payload))
        
        return schemas.BookResponse(**resp)
    finally:
        r.delete(lock_key)
