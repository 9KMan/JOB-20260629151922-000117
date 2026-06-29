id              SERIAL PK
target_id       INT FK
started_at      TIMESTAMPTZ
finished_at     TIMESTAMPTZ
status          TEXT        -- 'success' | 'failed' | 'partial'
records_count   INT
error_message   TEXT
