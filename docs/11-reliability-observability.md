# Reliability & Observability

SLO examples:
- booking success 99.9%
- availability p95 < 150ms (cached)
- reminder delivery within 2 minutes: 99%

Patterns:
- circuit breakers for external providers
- DLQ for async consumers
- correlation IDs + tracing
- metrics on conflicts, lock waits, queue lag
