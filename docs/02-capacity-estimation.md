# Capacity Estimation (back-of-the-envelope)

Example mid-size network:
- 3,000 providers
- 50,000 appointments/day
- Booking peak: 200–500 QPS
- Availability peak: 1,000–5,000 QPS
- Notifications: ~100k/day (confirm + reminder)

Storage:
- ~18M appointments/year
- Audit events: 5–10x rows depending on compliance

Insight:
- Search/availability is read-heavy → cache + precompute
- Booking is correctness-heavy → transactions/locks/idempotency

Next: `docs/03-domain-model.md`
