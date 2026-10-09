from typing import Any

def merge_clarifications(original_question: str, turns: list[dict[str, str]]) -> dict[str, Any]:
    resolved = original_question.strip()
    for turn in turns:
        resolved += f"\nClarification — {turn['question']} Answer — {turn['answer']}"
    return {"original_question": original_question, "clarification_turns": turns, "resolved_question": resolved}
