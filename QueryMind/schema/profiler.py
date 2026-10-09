def profile_schema(schema: dict) -> dict:
    return {
        "table_count": len(schema.get("tables", {})),
        "total_rows": sum(t.get("row_count", 0) for t in schema.get("tables", {}).values()),
        "columns_by_table": {name: [c["name"] for c in t["columns"]] for name, t in schema.get("tables", {}).items()},
    }
