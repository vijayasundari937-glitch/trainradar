-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- ── Train Positions ───────────────────────────────────────
-- Stores live GPS positions of every train
-- This will receive thousands of rows per minute
CREATE TABLE IF NOT EXISTS train_positions (
    time         TIMESTAMPTZ      NOT NULL,
    train_id     VARCHAR(64)      NOT NULL,
    trip_id      VARCHAR(64),
    route_id     VARCHAR(64),
    latitude     DOUBLE PRECISION NOT NULL,
    longitude    DOUBLE PRECISION NOT NULL,
    speed_kmh    FLOAT,
    bearing      FLOAT,
    occupancy    VARCHAR(32),
    source       VARCHAR(32)      NOT NULL DEFAULT 'unknown',
    raw_payload  JSONB,
    created_at   TIMESTAMPTZ      DEFAULT NOW()
);

-- Convert to a TimescaleDB hypertable
-- This means TimescaleDB will automatically split the data
-- into chunks by time — making time-based queries very fast
SELECT create_hypertable(
    'train_positions',
    'time',
    chunk_time_interval => INTERVAL '1 day',
    if_not_exists => TRUE
);

-- Indexes make lookups faster
CREATE INDEX IF NOT EXISTS idx_positions_train_id
    ON train_positions (train_id, time DESC);

CREATE INDEX IF NOT EXISTS idx_positions_route_id
    ON train_positions (route_id, time DESC);

-- ── Trip Updates ──────────────────────────────────────────
-- Stores delay information for each train at each stop
CREATE TABLE IF NOT EXISTS trip_updates (
    time             TIMESTAMPTZ  NOT NULL,
    trip_id          VARCHAR(64)  NOT NULL,
    route_id         VARCHAR(64),
    stop_id          VARCHAR(64),
    stop_sequence    INTEGER,
    arrival_delay    INTEGER,
    departure_delay  INTEGER,
    arrival_time     TIMESTAMPTZ,
    departure_time   TIMESTAMPTZ,
    schedule_rel     VARCHAR(32),
    source           VARCHAR(32)  NOT NULL DEFAULT 'gtfs-rt',
    raw_payload      JSONB,
    created_at       TIMESTAMPTZ  DEFAULT NOW()
);

SELECT create_hypertable(
    'trip_updates',
    'time',
    chunk_time_interval => INTERVAL '1 day',
    if_not_exists => TRUE
);

CREATE INDEX IF NOT EXISTS idx_trip_updates_trip_id
    ON trip_updates (trip_id, time DESC);

-- ── Service Alerts ────────────────────────────────────────
-- Stores disruption alerts (delays, cancellations etc)
CREATE TABLE IF NOT EXISTS service_alerts (
    id               SERIAL       PRIMARY KEY,
    alert_id         VARCHAR(128) NOT NULL UNIQUE,
    effect           VARCHAR(64),
    cause            VARCHAR(64),
    header_text      TEXT,
    description_text TEXT,
    route_ids        TEXT[],
    stop_ids         TEXT[],
    active_from      TIMESTAMPTZ,
    active_until     TIMESTAMPTZ,
    source           VARCHAR(32)  NOT NULL DEFAULT 'gtfs-rt',
    raw_payload      JSONB,
    created_at       TIMESTAMPTZ  DEFAULT NOW()
);

-- ── Train Schedules ───────────────────────────────────────
-- Stores static timetable data
CREATE TABLE IF NOT EXISTS train_schedules (
    id             SERIAL       PRIMARY KEY,
    trip_id        VARCHAR(64)  NOT NULL,
    route_id       VARCHAR(64)  NOT NULL,
    service_id     VARCHAR(64),
    headsign       VARCHAR(256),
    stop_id        VARCHAR(64)  NOT NULL,
    stop_sequence  INTEGER      NOT NULL,
    arrival_time   VARCHAR(8),
    departure_time VARCHAR(8),
    source         VARCHAR(32)  NOT NULL DEFAULT 'gtfs-static',
    created_at     TIMESTAMPTZ  DEFAULT NOW(),
    UNIQUE (trip_id, stop_sequence)
);

-- ── Ingestion Log ─────────────────────────────────────────
-- Tracks every ingestion batch — how many records came in,
-- how many succeeded, how many failed
CREATE TABLE IF NOT EXISTS ingestion_log (
    time               TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    source             VARCHAR(64) NOT NULL,
    event_type         VARCHAR(64) NOT NULL,
    records_received   INTEGER     DEFAULT 0,
    records_processed  INTEGER     DEFAULT 0,
    records_failed     INTEGER     DEFAULT 0,
    duration_ms        INTEGER,
    error_message      TEXT,
    metadata           JSONB
);

SELECT create_hypertable(
    'ingestion_log',
    'time',
    chunk_time_interval => INTERVAL '7 days',
    if_not_exists => TRUE
);