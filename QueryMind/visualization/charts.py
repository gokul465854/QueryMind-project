import pandas as pd
from pandas.api.types import is_numeric_dtype

def suggest_chart(df: pd.DataFrame):
    if len(df.columns) < 2 or df.empty:
        return None
    categorical = [c for c in df.columns if not is_numeric_dtype(df[c])]
    numeric = [c for c in df.columns if is_numeric_dtype(df[c])]
    if categorical and numeric:
        return ("bar", categorical[0], numeric[0])
    if len(numeric) >= 2:
        return ("bar", numeric[0], numeric[1])
    return None
