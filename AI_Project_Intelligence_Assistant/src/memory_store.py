
import os

import psycopg
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    """Connect to the PostgreSQL database."""
    required = ["PGHOST", "PGDATABASE", "PGUSER", "PGPASSWORD"]
    missing = [name for name in required if not os.getenv(name)]

    if missing:
        raise ValueError(
            "Missing PostgreSQL settings in .env: "
            + ", ".join(missing)
        )

    return psycopg.connect(
        host=os.getenv("PGHOST"),
        port=int(os.getenv("PGPORT", "5432")),
        dbname=os.getenv("PGDATABASE"),
        user=os.getenv("PGUSER"),
        password=os.getenv("PGPASSWORD"),
        connect_timeout=10,
    )


def initialize_memory_db():
    """Create persistent conversation-memory tables."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    conversation_id TEXT PRIMARY KEY,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS conversation_messages (
                    id BIGSERIAL PRIMARY KEY,
                    conversation_id TEXT NOT NULL
                        REFERENCES conversations(conversation_id)
                        ON DELETE CASCADE,
                    role TEXT NOT NULL
                        CHECK (role IN ('user', 'assistant')),
                    content TEXT NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
            """)

            cur.execute("""
                CREATE INDEX IF NOT EXISTS
                idx_conversation_messages_history
                ON conversation_messages (conversation_id, id);
            """)


def get_recent_messages(conversation_id, limit=10):
    """Retrieve recent conversation messages in chronological order."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT role, content
                FROM (
                    SELECT id, role, content
                    FROM conversation_messages
                    WHERE conversation_id = %s
                    ORDER BY id DESC
                    LIMIT %s
                ) AS recent
                ORDER BY id ASC;
            """, (conversation_id, limit))

            rows = cur.fetchall()

    return [
        {"role": role, "content": content}
        for role, content in rows
    ]


def save_exchange(conversation_id, question, answer):
    """Persist a question and its answer."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO conversations (conversation_id)
                VALUES (%s)
                ON CONFLICT (conversation_id) DO NOTHING;
            """, (conversation_id,))

            cur.execute("""
                INSERT INTO conversation_messages
                    (conversation_id, role, content)
                VALUES
                    (%s, 'user', %s),
                    (%s, 'assistant', %s);
            """, (
                conversation_id,
                question,
                conversation_id,
                answer,
            ))
