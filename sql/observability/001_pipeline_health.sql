CREATE OR REPLACE VIEW raw.vw_pipeline_health AS
SELECT
    run_id,
    started_at,
    finished_at,
    status,
    extract(epoch FROM (coalesce(finished_at, now()) - started_at)) AS duration_seconds,
    rows_read,
    rows_loaded,
    rows_rejected,
    rows_rejected::numeric / NULLIF(rows_read, 0) AS rejection_rate,
    error_message
FROM raw.ingestion_runs;

CREATE OR REPLACE VIEW raw.vw_rejections_by_rule AS
SELECT
    date_trunc('day', rejected_at) AS rejection_date,
    source_name,
    error_code,
    count(*) AS rejected_rows
FROM raw.rejections
CROSS JOIN LATERAL unnest(error_codes) AS error_code
GROUP BY 1, 2, 3;

CREATE OR REPLACE VIEW raw.vw_data_freshness AS
SELECT
    source_name,
    max(ingested_at) AS last_ingested_at,
    now() - max(ingested_at) AS age,
    count(*) AS total_versions
FROM raw.source_records
GROUP BY source_name;
