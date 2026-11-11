"""Database manager handling idempotency and run records."""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Dict


class DatabaseManager:
    def __init__(self, db_path: str = "trendbharat.db"):
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def _conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_db(self):
        schema_file = Path(__file__).parent / "schema.sql"
        with self._conn() as conn:
            conn.executescript(schema_file.read_text(encoding="utf-8"))

    def check_already_run_today(self, run_date: str) -> bool:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT id FROM daily_runs WHERE run_date = ? AND status = 'completed'", (run_date,)
            ).fetchone()
            return row is not None

    def record_run(self, run_date: str, story: Dict, status: str = "completed"):
        with self._conn() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO daily_runs (run_date, topic, category, headline, image_url, status)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    run_date,
                    story.get("query", ""),
                    story.get("category", ""),
                    story.get("headline", ""),
                    story.get("hd_image_url", ""),
                    status,
                ),
            )
