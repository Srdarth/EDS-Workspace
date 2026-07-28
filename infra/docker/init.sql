-- EddY — Schema PostgreSQL (espelho analítico do SQLite)
-- Uso: análises pesadas, dashboards, relatórios multi-drive
-- O banco canônico de produção é SQLite (eddy.db) — não usar PostgreSQL como source of truth

CREATE TABLE IF NOT EXISTS files (
    id          BIGSERIAL PRIMARY KEY,
    path        TEXT NOT NULL UNIQUE,
    filename    TEXT,
    ext         TEXT,
    size        BIGINT,
    kind        TEXT,
    status      TEXT DEFAULT 'new',
    hash        TEXT,
    sha256      TEXT,
    quicksig    TEXT,
    content_id  TEXT,
    source      TEXT,
    mtime_ns    BIGINT,
    title       TEXT,
    keywords    TEXT,
    text_preview TEXT,
    canonical_name TEXT,
    name_confidence INTEGER,
    duplicate_of TEXT,
    organized_path TEXT,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_files_status ON files(status);
CREATE INDEX IF NOT EXISTS idx_files_kind   ON files(kind);
CREATE INDEX IF NOT EXISTS idx_files_sha256 ON files(sha256);
CREATE INDEX IF NOT EXISTS idx_files_source ON files(source);
CREATE INDEX IF NOT EXISTS idx_files_qs     ON files(quicksig);

CREATE TABLE IF NOT EXISTS runs (
    id          BIGSERIAL PRIMARY KEY,
    run_key     TEXT,
    stage       TEXT,
    status      TEXT,
    started_at  TIMESTAMPTZ,
    finished_at TIMESTAMPTZ,
    details     JSONB
);

COMMENT ON TABLE files IS 'Mirror analítico do eddy.db SQLite para consultas pesadas';
COMMENT ON TABLE runs  IS 'Histórico de execuções do pipeline EddY';
