# Domain Model

Entities:
- Patient
- Provider
- Location/Facility/Clinic
- Provider Schedule (shift/break/block)
- Appointment (status machine)
- VisitType (duration, buffers, rules)
- Waitlist entry
- Audit events

Status machine (simplified):
- HELD → CONFIRMED → CHECKED_IN → COMPLETED
- CANCELLED / NO_SHOW / EXPIRED

Next: `docs/04-api-design.md`
