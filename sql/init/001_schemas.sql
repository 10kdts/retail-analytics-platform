CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS marts;

CREATE TABLE IF NOT EXISTS raw.ingestion_runs (
    run_id uuid PRIMARY KEY,
    started_at timestamptz NOT NULL DEFAULT now(),
    finished_at timestamptz,
    status text NOT NULL CHECK (status IN ('running', 'succeeded', 'failed')),
    source_directory text NOT NULL,
    rows_read integer NOT NULL DEFAULT 0,
    rows_loaded integer NOT NULL DEFAULT 0,
    rows_rejected integer NOT NULL DEFAULT 0,
    error_message text
);

CREATE TABLE IF NOT EXISTS raw.source_records (
    source_record_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    run_id uuid NOT NULL REFERENCES raw.ingestion_runs(run_id),
    source_name text NOT NULL,
    source_row_number integer NOT NULL,
    row_hash char(64) NOT NULL,
    payload jsonb NOT NULL,
    ingested_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (source_name, row_hash)
);

CREATE TABLE IF NOT EXISTS raw.rejections (
    rejection_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    run_id uuid NOT NULL REFERENCES raw.ingestion_runs(run_id),
    source_name text NOT NULL,
    source_row_number integer NOT NULL,
    row_hash char(64) NOT NULL,
    payload jsonb NOT NULL,
    error_codes text[] NOT NULL,
    rejected_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (source_name, row_hash, error_codes)
);

CREATE INDEX IF NOT EXISTS idx_source_records_run ON raw.source_records(run_id);
CREATE INDEX IF NOT EXISTS idx_rejections_run ON raw.rejections(run_id);
