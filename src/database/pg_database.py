import os
import psycopg2
from psycopg2.extras import Json
from typing import Optional
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("NEON_DB_URL")

def save_to_postgres(
    url: str,
    content: Optional[str] = None,
    summary: Optional[str] = None,
    source: Optional[str] = None,
    metadata: Optional[dict] = None
) -> str:
    if not content and not summary:
        raise ValueError("At least one of content or summary must be provided.")

    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    # Check if the URL already exists
    cur.execute("SELECT 1 FROM scraped_content WHERE url = %s", (url,))
    if cur.fetchone():
        cur.close()
        conn.close()
        return "Already Indexed. Thanks for sending!"

    # Insert the new data
    cur.execute(
        """
        INSERT INTO scraped_content (url, content, summary, source, metadata)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (url, content, summary, source, Json(metadata) if metadata else None)
    )
    conn.commit()
    cur.close()
    conn.close()

    return "Indexed and saved to database ✅"

def get_by_url(url: str):
    conn = psycopg2.connect(DATABASE_URL)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM scraped_content WHERE url = %s", (url,))
            row = cur.fetchone()
            return row
    finally:
        conn.close()
