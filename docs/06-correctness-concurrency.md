# Correctness & Concurrency (make-or-break)

Problem: two clients book the same slot at once.

Recommended baseline:
- DB transaction
- lock granularity: provider+day (or provider+slot)
- conflict check with row locks and/or constraints
- idempotency keys for retries

Optionally:
- short holds (2–5 minutes) in Redis + DB
- reschedule is atomic (new confirm + old cancel), or saga with compensation
