from llm.client import chat
from llm.prompts import QUERY_ANALYSIS_PROMPT, build_user_prompt
from llm.structured_output import parse_json_object

def generate_sql(question: str, schema_text: str) -> dict:
    raw = chat(QUERY_ANALYSIS_PROMPT, build_user_prompt(question, schema_text))
    result = parse_json_object(raw)
    if not isinstance(result.get("sql", ""), str):
        raise ValueError("LLM response is missing a valid SQL field.")
    for key in ("intent", "explanation"):
        result.setdefault(key, "")
    for key in ("tables_used", "columns_used"):
        if not isinstance(result.get(key, []), list):
            result[key] = []
    return result
