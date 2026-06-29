id              SERIAL PK
target_id       INT FK
external_id     TEXT
payload         JSONB
error           TEXT
failed_at       TIMESTAMPTZ
retry_count     INT
