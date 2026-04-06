-- Service contracts (quotation / proposal PDF registry). Applied by database.bootstrap_postgresql_schema() / scripts/bootstrap_postgres_schema.py.
CREATE TABLE IF NOT EXISTS contracts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contract_number TEXT,
    status TEXT,
    client_id UUID,
    project_name TEXT,
    company_name TEXT,
    client_name TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS ix_contracts_created_at ON contracts (created_at DESC);
CREATE INDEX IF NOT EXISTS ix_contracts_payload_client_id ON contracts ((payload->>'client_id'));
