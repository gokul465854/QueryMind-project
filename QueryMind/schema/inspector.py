import sqlite3
from pathlib import Path

def inspect_database(db_path: str) -> dict:
    path = Path(db_path).resolve()
    if not path.is_file():
        raise FileNotFoundError("Database file was not found.")
    uri = f"file:{path.as_posix()}?mode=ro"
    with sqlite3.connect(uri, uri=True, timeout=5) as conn:
        conn.row_factory = sqlite3.Row
        table_rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        ).fetchall()
        tables, relationships, lines = {}, [], [f"Database: {path.name}"]
        for row in table_rows:
            name = row["name"]
            escaped = name.replace('"', '""')
            columns = [dict(c) for c in conn.execute(f'PRAGMA table_info("{escaped}")').fetchall()]
            fks = [dict(fk) for fk in conn.execute(f'PRAGMA foreign_key_list("{escaped}")').fetchall()]
            count = conn.execute(f'SELECT COUNT(*) FROM "{escaped}"').fetchone()[0]
            sample = [dict(r) for r in conn.execute(f'SELECT * FROM "{escaped}" LIMIT 3').fetchall()]
            tables[name] = {"columns": columns, "foreign_keys": fks, "row_count": count, "sample_rows": sample}
            lines.append(f"\n{name} ({count} rows)")
            for col in columns:
                pk = " PRIMARY KEY" if col["pk"] else ""
                lines.append(f"- {col['name']} {col['type'] or 'ANY'}{pk}")
            for fk in fks:
                relationships.append({"table": name, "column": fk["from"], "references_table": fk["table"], "references_column": fk["to"]})
        if not tables:
            lines.append("(No user tables found)")
        return {"database_name": path.name, "tables": tables, "relationships": relationships, "schema_text": "\n".join(lines)}
