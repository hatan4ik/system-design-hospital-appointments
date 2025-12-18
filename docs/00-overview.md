# Overview

Hospitals are **scheduling factories** with strict constraints:
- Resources: doctors, rooms, equipment, staff
- Time slots: multiple calendars, time zones, shifts
- Rules: visit types, durations, buffers, eligibility, insurance, referrals
- Hard correctness requirement: **no double booking**, even under concurrency

Core systems:
1) Appointment Booking API (patient + staff)
2) Scheduling/Availability (compute or precompute)
3) Notifications (async)
4) Integrations (EHR/EMR, insurance)
5) Admin tooling + auditing

Start: `docs/01-requirements.md`
