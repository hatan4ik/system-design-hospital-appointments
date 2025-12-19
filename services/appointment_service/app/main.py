from typing import Optional

from fastapi import FastAPI, Header, HTTPException
from . import schemas, services

app = FastAPI(title="appointment-service")

@app.get("/healthz")
def healthz():
    return {"ok": True}

@app.post("/appointments", response_model=schemas.BookResponse)
async def book(req: schemas.BookRequest, idempotency_key: Optional[str] = Header(default=None, alias="Idempotency-Key")):
    if not idempotency_key:
        raise HTTPException(status_code=400, detail="Idempotency-Key required")
    
    return await services.book_appointment(req, idempotency_key)

@app.get("/appointments/{appointment_id}", response_model=schemas.Appointment)
async def get_appointment(appointment_id: str):
    return await services.get_appointment(appointment_id)