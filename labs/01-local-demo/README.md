# Lab 01 — Local Demo

Start:
```bash
docker compose up --build
```

Try:
```bash
curl -s "localhost:8080/availability?provider_id=prov_1&start=2025-12-18T15:00:00Z&end=2025-12-18T18:00:00Z&slot_minutes=15" | jq
curl -s -X POST localhost:8080/appointments   -H 'content-type: application/json'   -H 'Idempotency-Key: 11111111-1111-1111-1111-111111111111'   -d '{"patient_id":"pat_1","provider_id":"prov_1","visit_type":"FOLLOW_UP_15","start_ts":"2025-12-18T15:00:00Z","end_ts":"2025-12-18T15:15:00Z","location_id":"loc_1"}' | jq
```
