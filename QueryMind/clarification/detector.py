import re

def detect_ambiguity(question: str, schema: dict | None = None) -> dict:
    """Lightweight deterministic pre-check; LLM-based clarification can be added later."""
    q = question.strip().lower()
    if not q:
        return {"needs_clarification": True, "reason": "The question is empty.", "question": "What would you like to know from the database?"}
    if re.search(r"\b(top|best|highest|lowest|most|least)\b", q) and not re.search(r"\b(by|based on|according to|marks|revenue|salary|count|orders|score|date|price)\b", q):
        return {"needs_clarification": True, "reason": "The ranking criterion is unclear.", "question": "What should the results be ranked by?"}
    if re.search(r"\b(recent|latest|old|new|last)\b", q) and not re.search(r"\b(day|week|month|year|date|time|created|updated|202\d)\b", q):
        return {"needs_clarification": True, "reason": "The time condition may be underspecified.", "question": "What time period or date column should I use?"}
    return {"needs_clarification": False, "reason": "", "question": ""}
