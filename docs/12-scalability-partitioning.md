# Scalability & Partitioning

- Scale reads with cache + read replicas
- Partition appointments by facility/time (month)
- Reduce contention with provider+day locks
- Handle hot providers with queueing/backpressure
- Multi-region: keep booking local per region; replicate read models async
