import sqlite3
import pandas as pd
from pathlib import Path
from sql.validator import validate_read_only_sql

MAX_ROWS = 200

def execute_read_only(db_path: str, sql: str, timeout_seconds: float = 5.0) -> pd.DataFrame:
    path = Path(db_path).resolve()
    validation = validate_read_only_sql(sql)
    if not validation["valid"]:
        raise ValueError(validation["message"])
    uri = f"file:{path.as_posix()}?mode=ro"
    with sqlite3.connect(uri, uri=True, timeout=timeout_seconds) as conn:
        conn.set_authorizer(_read_only_authorizer)
        conn.set_progress_handler(lambda: 1, 100000)
        cursor = conn.execute(validation.get("sql", sql))
        columns = [col[0] for col in cursor.description or []]
        rows = cursor.fetchmany(MAX_ROWS + 1)
        if len(rows) > MAX_ROWS:
            rows = rows[:MAX_ROWS]
        return pd.DataFrame(rows, columns=columns)

def _read_only_authorizer(action, arg1, arg2, database, source):
    allowed = {
        sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ, sqlite3.SQLITE_FUNCTION,
        sqlite3.SQLITE_RECURSIVE,
    }
    if action in allowed:
        return sqlite3.SQLITE_OK
    return sqlite3.SQLITE_DENY
