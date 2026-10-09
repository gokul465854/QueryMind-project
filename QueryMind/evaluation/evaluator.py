from evaluation.metrics import binary_metrics

def evaluate_clarification(predicted: list[bool], expected: list[bool]) -> dict:
    if len(predicted) != len(expected):
        raise ValueError("Predicted and expected labels must have equal length.")
    tp = sum(p and e for p, e in zip(predicted, expected))
    fp = sum(p and not e for p, e in zip(predicted, expected))
    fn = sum(not p and e for p, e in zip(predicted, expected))
    return binary_metrics(tp, fp, fn)
