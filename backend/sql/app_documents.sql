-- Generic document store for dashboard (and future module migrations).
-- Rows: collection name + logical doc_id + JSONB payload (+ created_at for ordering).
CREATE TABLE IF NOT EXISTS app_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    collection TEXT NOT NULL,
    doc_id TEXT NOT NULL,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ,
    UNIQUE (collection, doc_id)
);

CREATE INDEX IF NOT EXISTS ix_app_documents_collection_created
    ON app_documents (collection, created_at DESC);
CREATE INDEX IF NOT EXISTS ix_app_documents_coll_status
    ON app_documents (collection, ((payload->>'status')));
CREATE INDEX IF NOT EXISTS ix_app_documents_coll_auditor
    ON app_documents (collection, ((payload->>'auditor_id')));
