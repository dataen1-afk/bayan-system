-- Organization clients (PostgreSQL). Also ensured at startup via database.connect_db().
CREATE TABLE IF NOT EXISTS clients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_name TEXT,
    national_address TEXT,
    tax_number TEXT,
    mobile TEXT,
    email TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS ix_clients_created_at ON clients (created_at DESC);
