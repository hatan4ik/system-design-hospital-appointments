import json
import uuid
from datetime import datetime
from . import schemas

async def get_idempotency_key(conn, idempotency_key: str):
    return await conn.fetchrow(
        "SELECT request_hash, response_ref FROM idempotency_keys WHERE idempotency_key = $1",
        idempotency_key,
    )

async def create_idempotency_key(conn, idempotency_key: str, user_id: str, request_hash: str, response: dict):
    await conn.execute(
        """
        INSERT INTO idempotency_keys(idempotency_key, user_id, request_hash, response_ref)
        VALUES ($1,$2,$3,$4)
        """,
        idempotency_key, user_id, request_hash, json.dumps(response),
    )

async def check_appointment_conflict(conn, provider_id: str, start_ts: datetime, end_ts: datetime) -> bool:
    return await conn.fetchrow(
        """
        SELECT 1 FROM appointments
        WHERE provider_id = $1
          AND status IN ('HELD','CONFIRMED')
          AND NOT (end_ts <= $2 OR start_ts >= $3)
        LIMIT 1
        """,
        provider_id, start_ts, end_ts,
    ) is not None

async def create_appointment(conn, req: schemas.BookRequest) -> str:
    apt_id = f"apt_{uuid.uuid4().hex[:12]}"
    await conn.execute(
        """
        INSERT INTO appointments(id, patient_id, provider_id, start_ts, end_ts, status, visit_type, location_id)
        VALUES ($1,$2,$3,$4,$5,'CONFIRMED',$6,$7)
        """,
        apt_id, req.patient_id, req.provider_id, req.start_ts, req.end_ts, req.visit_type, req.location_id,
    )
    return apt_id

async def create_appointment_audit(conn, appointment_id: str, actor_id: str, req: schemas.BookRequest):
    await conn.execute(
        """
        INSERT INTO appointment_audit(appointment_id, actor_id, action, payload)
        VALUES ($1,$2,'APPOINTMENT_CREATED',$3::jsonb)
        """,
        appointment_id, actor_id, json.dumps(req.model_dump(mode="json")),
    )

async def get_appointment(conn, appointment_id: str):
    return await conn.fetchrow(
        "SELECT id, patient_id, provider_id, start_ts, end_ts, status, visit_type, location_id FROM appointments WHERE id = $1",
        appointment_id,
    )
