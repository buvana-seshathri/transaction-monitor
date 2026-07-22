"""
SQLite storage for scored transactions.

Keeps things simple: one table, a handful of functions. No ORM - just
plain sqlite3, since the schema is small and unlikely to change.
"""

import sqlite3

DB_PATH = "transactions.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id TEXT PRIMARY KEY,
    timestamp TEXT NOT NULL,
    amount REAL NOT NULL,
    merchant_category TEXT NOT NULL,
    is_anomaly INTEGER NOT NULL,
    anomaly_score REAL NOT NULL,
    is_seed_anomaly INTEGER NOT NULL
);
"""


def get_connection():
    """Open a connection with row access by column name."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the transactions table if it doesn't exist yet."""
    conn = get_connection()
    conn.execute(SCHEMA)
    conn.commit()
    conn.close()


def insert_transaction(transaction, is_anomaly, anomaly_score):
    """Save one scored transaction to the database."""
    conn = get_connection()
    conn.execute(
        """
        INSERT OR REPLACE INTO transactions
            (transaction_id, timestamp, amount, merchant_category,
             is_anomaly, anomaly_score, is_seed_anomaly)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            transaction["transaction_id"],
            transaction["timestamp"],
            transaction["amount"],
            transaction["merchant_category"],
            int(is_anomaly),
            anomaly_score,
            int(transaction.get("is_seed_anomaly", False)),
        ),
    )
    conn.commit()
    conn.close()


def get_recent(limit=50):
    """Most recent transactions, newest first."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM transactions ORDER BY timestamp DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_anomalies(limit=50):
    """Most recent flagged transactions only."""
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT * FROM transactions
        WHERE is_anomaly = 1
        ORDER BY timestamp DESC LIMIT ?
        """,
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


if __name__ == "__main__":
    # Quick sanity check when running this file directly
    init_db()
    print(f"Database ready at {DB_PATH}")
