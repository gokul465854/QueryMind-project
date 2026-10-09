import json
import re

def parse_json_object(text: str) -> dict:
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", cleaned, flags=re.IGNORECASE)
    try:
        obj = json.loads(cleaned)
    except json.JSONDecodeError:
        start, end = cleaned.find("{"), cleaned.rfind("}")
        if start < 0 or end <= start:
            raise ValueError("LLM response did not contain a JSON object.")
        obj = json.loads(cleaned[start:end + 1])
    if not isinstance(obj, dict):
        raise ValueError("LLM response must be a JSON object.")
    return obj
