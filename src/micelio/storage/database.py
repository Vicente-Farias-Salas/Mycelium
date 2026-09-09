"""DatabaseManager for thread-safe SQLite storage with WAL mode enabled."""

from pathlib import Path
import sqlite3


class DatabaseManager:
    """Manages SQLite database connections and schema initialization."""

    def __init__(self, db_path: Path | str = "data/micelio.db") -> None:
        self._db_path = Path(db_path)
        self._db_path.parent.mkdir(parents=True, exist_ok=True)

    def get_connection(self) -> sqlite3.Connection:
        """Create and return a configured connection with WAL mode and row factory."""
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        return conn

    def initialize_schema(self) -> None:
        """Execute DDL schema creation statements."""
        with self.get_connection() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    vision TEXT NOT NULL,
                    creator_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    shared_contracts_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS nutrients (
                    project_id TEXT PRIMARY KEY,
                    distilled_specs TEXT NOT NULL,
                    interfaces_json TEXT NOT NULL,
                    constraints_json TEXT NOT NULL,
                    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS memberships (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    member_id TEXT NOT NULL,
                    role_in_project TEXT NOT NULL,
                    status TEXT NOT NULL,
                    local_workspace_path TEXT NOT NULL,
                    invited_at TEXT NOT NULL,
                    joined_at TEXT,
                    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS synapse_events (
                    event_id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    source_agent_id TEXT NOT NULL,
                    target_agent_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
                );
                """
            )
