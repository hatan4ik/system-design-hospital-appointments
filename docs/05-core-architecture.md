# Core Architecture

Services:
- API Gateway (auth/rate limit)
- Appointment Service (book/cancel/reschedule; correctness)
- Availability Service (fast reads, caching, precompute option)
- Provider Schedule Service
- Notification Service (async)
- Waitlist Service (async)
- Audit/Event Service (immutable log)
- Integration Service (EHR/insurance)

Stores:
- Postgres OLTP for bookings
- Redis for cache + short holds
- Event bus (Kafka/SNS+SQS/EventBridge)
- Search index for provider discovery

Next: `docs/06-correctness-concurrency.md`
