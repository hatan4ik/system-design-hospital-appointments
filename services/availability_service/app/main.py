from datetime import datetime
from fastapi import FastAPI, Query
from . import services

app = FastAPI(title="availability-service")

@app.get("/healthz")
def healthz():
    return {"ok": True}

@app.get("/availability")
def availability(provider_id: str, start: datetime, end: datetime, slot_minutes: int = Query(15, ge=5, le=120)):
    return services.get_availability(provider_id, start, end, slot_minutes)