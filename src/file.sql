id              SERIAL PRIMARY KEY
target_id       INT REFERENCES scraper_targets(id)
run_id          INT REFERENCES runs(id)
payload         JSONB
error           TEXT NOT NULL
attempts        INT NOT NULL
failed_at       TIMESTAMPTZ NOT NULL DEFAULT now()
