# src/database/migrate_neon.py

import os
import psycopg2
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("NEON_DB_URL")

MIGRATION_SQL = """
CREATE TABLE IF NOT EXISTS scraped_content (
    id SERIAL PRIMARY KEY,
    url TEXT UNIQUE NOT NULL,
    content TEXT,
    summary TEXT,
    source TEXT,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for sorting/filtering
CREATE INDEX IF NOT EXISTS idx_scraped_created_at ON scraped_content(created_at);
"""

def run_migration():
    if not DATABASE_URL:
        raise EnvironmentError("❌ NEON_DB_URL is not set in environment variables.")

    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute(MIGRATION_SQL)
    conn.commit()
    cur.close()
    conn.close()
    print("✅ Migration complete: Table + indexes created in Neon.")

if __name__ == "__main__":
    run_migration()