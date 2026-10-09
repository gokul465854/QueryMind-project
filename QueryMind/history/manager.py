import sqlite3
from datetime import datetime, timezone
from pathlib import Path

HISTORY_DB = Path(__file__).resolve().parent / "query_history.sqlite3"

def init_history() -> None:
    with sqlite3.connect(HISTORY_DB) as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS query_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            question TEXT NOT NULL,
            clarification TEXT NOT NULL,
            sql TEXT NOT NULL,
            status TEXT NOT NULL,
            execution_time REAL NOT NULL,
            retries INTEGER NOT NULL
        )""")

def add_history(question: str, clarification: list, sql: str, status: str, execution_time: float, retries: int) -> None:
    init_history()
    with sqlite3.connect(HISTORY_DB) as conn:
        conn.execute(
            "INSERT INTO query_history(timestamp, question, clarification, sql, status, execution_time, retries) VALUES(?,?,?,?,?,?,?)",
            (datetime.now(timezone.utc).isoformat(), question, repr(clarification), sql, status, execution_time, retries),
        )

def get_history(limit: int = 20) -> list[dict]:
    init_history()
    with sqlite3.connect(HISTORY_DB) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM query_history ORDER BY id DESC LIMIT ?", (max(1, min(limit, 100)),)).fetchall()
        return [dict(r) for r in rows]
