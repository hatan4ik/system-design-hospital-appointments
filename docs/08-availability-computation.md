# Availability Computation

Approach A (simple): on-the-fly compute + cache per provider/day
Approach B (scale): precompute slots and book atomically against inventory
Caching:
- short TTL + event-driven invalidation
- stale-while-revalidate for UX

Next: `docs/09-notifications-waitlist.md`
