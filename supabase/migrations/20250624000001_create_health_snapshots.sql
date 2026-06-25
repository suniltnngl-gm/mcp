CREATE TABLE IF NOT EXISTS health_snapshots (
  id BIGSERIAL PRIMARY KEY,
  score INTEGER NOT NULL,
  categories JSONB DEFAULT '{}',
  open_findings INTEGER DEFAULT 0,
  critical_findings INTEGER DEFAULT 0,
  repo_count INTEGER DEFAULT 0,
  dirty_repos INTEGER DEFAULT 0,
  snapshot_at TIMESTAMPTZ DEFAULT now()
);

-- Index for time-series queries
CREATE INDEX IF NOT EXISTS idx_snapshots_at ON health_snapshots (snapshot_at DESC);

-- Enable Row Level Security
ALTER TABLE health_snapshots ENABLE ROW LEVEL SECURITY;

-- Allow authenticated users to read
CREATE POLICY "authenticated_read"
  ON health_snapshots
  FOR SELECT
  TO authenticated
  USING (true);

-- Allow service role to insert
CREATE POLICY "service_insert"
  ON health_snapshots
  FOR INSERT
  TO service_role
  WITH CHECK (true);
