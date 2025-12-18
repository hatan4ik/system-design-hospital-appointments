# Requirements (FAANG interview style)

## Functional (MVP)
- Search providers + locations + visit types
- View availability for a provider or clinic
- Book/cancel/reschedule an appointment
- Prevent double booking
- Confirmation + reminder notifications
- Waitlist (optional in MVP; great differentiator)

## Non-functional
- Correctness: strong consistency on booking writes
- Performance: availability reads should be fast (cacheable)
- Reliability: no corrupt bookings, graceful degradation
- Security/Privacy: PHI/PII protections + audits
- Observability: trace a booking end-to-end
- Extensible: multi-clinic, multi-facility, multi-tenant

## Clarifying questions
- Channels: patient app + call center?
- Appointment types/durations? buffers?
- Multi-resource visits? (room/equipment)
- Peak QPS and regions?
- Regulations: HIPAA/GDPR-like constraints?

Next: `docs/02-capacity-estimation.md`
