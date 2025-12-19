from pydantic import BaseModel
from datetime import datetime

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
