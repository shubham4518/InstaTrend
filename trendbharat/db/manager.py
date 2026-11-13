"""Database manager handling idempotency and run records for daily posts."""

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
            # Run column migration for existing databases
            try:
                conn.execute("ALTER TABLE daily_runs ADD COLUMN post_index INTEGER DEFAULT 1;")
            except sqlite3.OperationalError:
                pass

    def check_post_completed(self, run_date: str, post_index: int = 1) -> bool:
        """Checks if a specific post index for a date has already been completed."""
        with self._conn() as conn:
            row = conn.execute(
                "SELECT id FROM daily_runs WHERE run_date = ? AND post_index = ? AND status = 'completed'",
                (run_date, post_index),
            ).fetchone()
            return row is not None

    def check_all_completed_today(self, run_date: str, required_count: int = 3) -> bool:
        """Checks if all required daily posts have been completed."""
        with self._conn() as conn:
            row = conn.execute(
                "SELECT COUNT(*) AS cnt FROM daily_runs WHERE run_date = ? AND status = 'completed'",
                (run_date,),
            ).fetchone()
            count = row["cnt"] if row else 0
            return count >= required_count

    def check_already_run_today(self, run_date: str) -> bool:
        """Backward compatibility: checks if at least 1 post was recorded."""
        return self.check_all_completed_today(run_date, required_count=3)

    def record_run(self, run_date: str, story: Dict, post_index: int = 1, status: str = "completed"):
        with self._conn() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO daily_runs
                   (run_date, post_index, topic, category, headline, image_url, status)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    run_date,
                    post_index,
                    story.get("query", ""),
                    story.get("category", ""),
                    story.get("headline", ""),
                    story.get("hd_image_url", ""),
                    status,
                ),
            )
