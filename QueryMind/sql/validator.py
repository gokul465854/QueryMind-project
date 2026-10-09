import sqlglot
from sqlglot import exp

FORBIDDEN = (
    exp.Insert, exp.Update, exp.Delete, exp.Create, exp.Drop, exp.Alter,
    exp.Command, exp.Transaction, exp.Merge,
)

def validate_read_only_sql(sql: str, schema: dict | None = None) -> dict:
    if not sql or not sql.strip():
        return {"valid": False, "message": "No SQL was generated."}
    try:
        parsed = sqlglot.parse(sql, read="sqlite")
    except Exception:
        return {"valid": False, "message": "SQL syntax could not be parsed."}
    if len(parsed) != 1 or parsed[0] is None:
        return {"valid": False, "message": "Only one SQL statement is allowed."}
    tree = parsed[0]
    if not isinstance(tree, exp.Select):
        return {"valid": False, "message": "Only SELECT queries are allowed."}
    if any(isinstance(node, FORBIDDEN) for node in tree.walk()):
        return {"valid": False, "message": "The query contains a prohibited operation."}
    for node in tree.walk():
        if isinstance(node, exp.Func) and node.sql_name().upper() in {"LOAD_EXTENSION"}:
            return {"valid": False, "message": "The query contains a prohibited function."}
    if schema:
        allowed = set(schema.get("tables", {}).keys())
        referenced = {t.name for t in tree.find_all(exp.Table)}
        unknown = referenced - allowed
        if unknown:
            return {"valid": False, "message": f"Unknown table(s): {', '.join(sorted(unknown))}"}
    if not any(isinstance(node, exp.Limit) for node in tree.walk()):
        tree = tree.limit(200)
    return {"valid": True, "message": "Parsed as a single read-only SELECT query.", "sql": tree.sql(dialect="sqlite")}
