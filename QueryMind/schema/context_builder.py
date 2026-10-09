def build_schema_context(schema: dict, max_sample_rows: int = 2) -> str:
    lines = [f"Database: {schema.get('database_name', 'unknown')}"]
    for table_name, info in schema.get("tables", {}).items():
        lines.append(f"Table {table_name}:")
        for col in info.get("columns", []):
            lines.append(f"  {col['name']} {col.get('type') or 'ANY'}" + (" PRIMARY KEY" if col.get("pk") else ""))
        for fk in info.get("foreign_keys", []):
            lines.append(f"  FOREIGN KEY {fk['from']} REFERENCES {fk['table']}({fk['to']})")
        for row in info.get("sample_rows", [])[:max_sample_rows]:
            lines.append(f"  sample: {row}")
    return "\n".join(lines)
