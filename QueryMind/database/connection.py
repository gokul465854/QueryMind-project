import sqlite3
from pathlib import Path
import tempfile

MAX_UPLOAD_BYTES = 50 * 1024 * 1024

def validate_sqlite_bytes(data: bytes, original_name: str) -> Path:
    suffix = Path(original_name).suffix.lower()
    if suffix not in {".db", ".sqlite", ".sqlite3"}:
        raise ValueError("Upload must be a .db, .sqlite, or .sqlite3 file.")
    if not data or len(data) > MAX_UPLOAD_BYTES:
        raise ValueError("Database file is empty or exceeds the 50 MB upload limit.")
    if not data.startswith(b"SQLite format 3\x00"):
        raise ValueError("The uploaded file does not have a valid SQLite header.")
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix, prefix="querymind_") as f:
        f.write(data)
        path = Path(f.name)
    try:
        with sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True) as conn:
            conn.execute("PRAGMA query_only=ON")
            conn.execute("SELECT name FROM sqlite_master LIMIT 1").fetchall()
    except Exception:
        path.unlink(missing_ok=True)
        raise ValueError("The uploaded SQLite database is corrupt or unreadable.")
    return path
