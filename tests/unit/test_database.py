"""Database SQLite optimization tests."""

import pytest
from pathlib import Path
from micelio.storage.database import DatabaseManager

def test_sqlite_pragmas_for_high_throughput(tmp_path: Path):
    """Verify that the database connection has the performance PRAGMAs applied."""
    db = DatabaseManager(db_path=tmp_path / "test.db")
    db.initialize_schema()
    
    with db.get_connection() as conn:
        # journal_mode in WAL might return "wal" or "memory" depending on environment, but let's check it doesn't crash
        jm = conn.execute("PRAGMA journal_mode;").fetchone()[0]
        sync = conn.execute("PRAGMA synchronous;").fetchone()[0]
        
        # PRAGMA synchronous=NORMAL returns 1
        assert sync == 1 or sync == "1"
        assert jm.lower() == "wal" or jm.lower() == "memory"
