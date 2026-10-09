from core.state import ConversationState

def record_answer(state: ConversationState, question: str, answer: str) -> ConversationState:
    state.add_clarification(question, answer)
    return state
