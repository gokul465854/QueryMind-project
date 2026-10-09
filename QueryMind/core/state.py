from dataclasses import dataclass, field
from typing import Any

@dataclass
class ConversationState:
    original_question: str
    clarification_turns: list[dict[str, str]] = field(default_factory=list)
    resolved_intent: dict[str, Any] = field(default_factory=dict)

    def add_clarification(self, question: str, answer: str) -> None:
        self.clarification_turns.append({"question": question, "answer": answer})
