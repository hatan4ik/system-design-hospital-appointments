-- Postgres baseline schema (simplified)
CREATE EXTENSION IF NOT EXISTS btree_gist;
CREATE TABLE IF NOT EXISTS patients (
  id TEXT PRIMARY KEY,
  full_name TEXT NOT NULL,
  phone TEXT,
  email TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS providers (
  id TEXT PRIMARY KEY,
  full_name TEXT NOT NULL,
  specialty TEXT NOT NULL,
  location_id TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS provider_schedules (
  id TEXT PRIMARY KEY,
  provider_id TEXT NOT NULL REFERENCES providers(id),
  start_ts TIMESTAMPTZ NOT NULL,
  end_ts TIMESTAMPTZ NOT NULL,
  kind TEXT NOT NULL, -- SHIFT/BREAK/BLOCK
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS appointments (
  id TEXT PRIMARY KEY,
  patient_id TEXT NOT NULL REFERENCES patients(id),
  provider_id TEXT NOT NULL REFERENCES providers(id),
  start_ts TIMESTAMPTZ NOT NULL,
  end_ts TIMESTAMPTZ NOT NULL,
  status TEXT NOT NULL,
  visit_type TEXT NOT NULL,
  location_id TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_appointments_provider_start ON appointments(provider_id, start_ts);
CREATE INDEX IF NOT EXISTS idx_appointments_patient_start ON appointments(patient_id, start_ts);
ALTER TABLE appointments
  ADD CONSTRAINT IF NOT EXISTS no_overlap_per_provider
  EXCLUDE USING gist (
    provider_id WITH =,
    tstzrange(start_ts, end_ts) WITH &&
  )
  WHERE (status IN ('HELD','CONFIRMED'));

CREATE TABLE IF NOT EXISTS idempotency_keys (
  idempotency_key TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  request_hash TEXT NOT NULL,
  response_ref TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS appointment_audit (
  id BIGSERIAL PRIMARY KEY,
  appointment_id TEXT NOT NULL,
  actor_id TEXT NOT NULL,
  action TEXT NOT NULL,
  ts TIMESTAMPTZ NOT NULL DEFAULT now(),
  payload JSONB NOT NULL
);
