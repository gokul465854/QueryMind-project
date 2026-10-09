"""Reserved for a bounded, validate-before-retry SQL self-correction phase."""

def correction_budget(max_retries: int = 3) -> int:
    return max(0, min(int(max_retries), 3))
