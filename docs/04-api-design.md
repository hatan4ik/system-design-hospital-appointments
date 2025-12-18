# API Design

Patient APIs:
- GET /providers?specialty=&location=
- GET /availability?provider_id=&from=&to=&visit_type=
- POST /appointments  (Idempotency-Key required)
- POST /appointments/{id}/cancel
- POST /appointments/{id}/reschedule
- GET /appointments/{id}

Staff APIs:
- schedule CRUD
- bulk reschedule tooling
- overrides with audit

Key principle:
- Availability reads can be cached / eventually consistent
- Booking writes must be strongly consistent

Next: `docs/05-core-architecture.md`
