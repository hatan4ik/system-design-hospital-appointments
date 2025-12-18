# API snippet

POST /appointments
Headers: Idempotency-Key: <uuid>
Body:
{
  "patient_id": "pat_1",
  "provider_id": "prov_1",
  "visit_type": "FOLLOW_UP_15",
  "start_ts": "2025-12-18T15:00:00Z",
  "end_ts": "2025-12-18T15:15:00Z",
  "location_id": "loc_1"
}
