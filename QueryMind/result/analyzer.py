import pandas as pd

def summarize_result(df: pd.DataFrame) -> str:
    if df.empty:
        return "The query completed successfully but returned no rows."
    if len(df.columns) == 0:
        return "The query completed successfully."
    if len(df) == 1 and len(df.columns) <= 3:
        values = ", ".join(f"{col}: {df.iloc[0][col]}" for col in df.columns)
        return f"Returned one result: {values}."
    return f"The query returned {len(df)} row(s) across {len(df.columns)} column(s)."
