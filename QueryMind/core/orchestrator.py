import time
from pathlib import Path
from schema.inspector import inspect_database
from sql.generator import generate_sql
from sql.validator import validate_read_only_sql
from sql.executor import execute_read_only
from result.analyzer import summarize_result

class QueryMindOrchestrator:
    def __init__(self, db_path: str):
        self.db_path = str(Path(db_path).resolve())

    def run(self, question: str) -> dict:
        started = time.perf_counter()
        schema = inspect_database(self.db_path)
        generated = generate_sql(question, schema["schema_text"])
        sql = generated["sql"]
        validation = validate_read_only_sql(sql, schema)
        if not validation["valid"]:
            return {
                "status": "rejected", "sql": sql, "intent": generated.get("intent", ""),
                "explanation": generated.get("explanation", ""), "tables_used": generated.get("tables_used", []),
                "columns_used": generated.get("columns_used", []), "validation_message": validation["message"],
                "message": "The generated query did not pass the read-only SQL safety checks.",
                "execution_time": time.perf_counter() - started, "retries": 0,
            }
        try:
            df = execute_read_only(self.db_path, sql)
            return {
                "status": "success", "sql": sql, "intent": generated.get("intent", ""),
                "explanation": generated.get("explanation", ""), "tables_used": generated.get("tables_used", []),
                "columns_used": generated.get("columns_used", []), "validation_message": validation["message"],
                "dataframe": df, "summary": summarize_result(df), "execution_time": time.perf_counter() - started,
                "retries": 0,
            }
        except Exception:
            return {
                "status": "error", "sql": sql, "intent": generated.get("intent", ""),
                "explanation": generated.get("explanation", ""), "tables_used": generated.get("tables_used", []),
                "columns_used": generated.get("columns_used", []), "validation_message": validation["message"],
                "message": "The SQL passed validation but could not be executed. Check the schema or revise the question.",
                "execution_time": time.perf_counter() - started, "retries": 0,
            }
