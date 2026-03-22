import pandas as pd

def clean_data(df: pd.DataFrame):
    df = df.drop_duplicates()

    for col in df.columns:

        # 🔥 Step 1: Try numeric first
        try:
            df[col] = pd.to_numeric(df[col])
            continue
        except:
            pass

        # 🔥 Step 2: Try datetime ONLY if likely date
        sample = df[col].astype(str).head(10)

        date_keywords = ["date", "time", "year", "month"]

        if any(word in col.lower() for word in date_keywords):
            converted = pd.to_datetime(
                df[col],
                errors='coerce',
            )

            # Only accept if most values are valid dates
            if converted.notna().sum() > len(df) * 0.6:
                df[col] = converted

        # 🔥 Step 3: Fill missing values
        if df[col].dtype == "object":
            df[col] = df[col].fillna("Unknown")
        else:
            df[col] = df[col].fillna(df[col].mean())

    return df