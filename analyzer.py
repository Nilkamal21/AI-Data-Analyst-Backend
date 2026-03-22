import pandas as pd

def analyze_data(df: pd.DataFrame):
    summary = {}

    summary["shape"] = {
        "rows": df.shape[0],
        "columns": df.shape[1]
    }

    summary["columns"] = list(df.columns)

    summary["dtypes"] = df.dtypes.astype(str).to_dict()

    summary["missing_values"] = df.isnull().sum().to_dict()

    # Identify column types
    numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns.tolist()
    categorical_cols = df.select_dtypes(include=["object"]).columns.tolist()
    datetime_cols = df.select_dtypes(include=["datetime64"]).columns.tolist()

    summary["numeric_columns"] = numeric_cols
    summary["categorical_columns"] = categorical_cols
    summary["datetime_columns"] = datetime_cols

    # Basic stats
    summary["statistics"] = df.describe().to_dict()

    return summary