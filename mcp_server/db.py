from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Optional

from models import KnownError, ParsedLog, Incident


DB_FILE = Path("incidents.db")

@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    """Context manager to get a SQLite connection with row access by name."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def init_db() -> None:
    """Create tables if they don't exist yet."""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS known_errors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fingerprint TEXT UNIQUE NOT NULL,
                error_type TEXT NOT NULL,
                service TEXT NOT NULL,
                description TEXT NOT NULL,
                suggested_fix TEXT NOT NULL,
                first_seen_at TEXT NOT NULL,
                last_seen_at TEXT NOT NULL,
                occurrences INTEGER NOT NULL DEFAULT 1
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fingerprint TEXT NOT NULL,
                service TEXT NOT NULL,
                environment TEXT NOT NULL,
                error_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                message TEXT NOT NULL,
                stack_summary TEXT NOT NULL,
                raw_log TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )

def get_known_error(fingerprint: str) -> Optional[KnownError]:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM known_errors WHERE fingerprint = ?",
            (fingerprint,),
        )
        row = cur.fetchone()
        if row is None:
            return None
        return KnownError(**dict(row))

def upsert_known_error(parsed: ParsedLog, description: str, suggested_fix: str) -> KnownError:
    """
    Insert or update a known error.
    For v1, if it exists we just bump occurrences and update last_seen_at.
    """
    with get_connection() as conn:
        cur = conn.cursor()
        # Try update
        cur.execute(
            """
            UPDATE known_errors
            SET last_seen_at = ?, occurrences = occurrences + 1
            WHERE fingerprint = ?
            """,
            (parsed["timestamp"], parsed["fingerprint"]),
        )
        if cur.rowcount == 0:
            # Insert new row
            cur.execute(
                """
                INSERT INTO known_errors (
                    fingerprint, error_type, service,
                    description, suggested_fix,
                    first_seen_at, last_seen_at, occurrences
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, 1)
                """,
                (
                    parsed["fingerprint"],
                    parsed["error_type"],
                    parsed["service"],
                    description,
                    suggested_fix,
                    parsed["timestamp"],
                    parsed["timestamp"],
                ),
            )
        # Return current row
        cur.execute(
            "SELECT * FROM known_errors WHERE fingerprint = ?",
            (parsed["fingerprint"],),
        )
        row = cur.fetchone()
        return KnownError(**dict(row))

def insert_incident(parsed: ParsedLog, raw_log_json: str) -> Incident:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO incidents (
                fingerprint, service, environment,
                error_type, severity, message,
                stack_summary, raw_log, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                parsed["fingerprint"],
                parsed["service"],
                parsed["environment"],
                parsed["error_type"],
                parsed["severity"],
                parsed["message"],
                parsed["stack_summary"],
                raw_log_json,
                parsed["timestamp"],
            ),
        )
        incident_id = cur.lastrowid
        cur.execute("SELECT * FROM incidents WHERE id = ?", (incident_id,))
        row = cur.fetchone()
        return Incident(**dict(row))
