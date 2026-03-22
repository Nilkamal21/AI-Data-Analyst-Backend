import pandas as pd

def clean_data(df: pd.DataFrame):
    df = df.drop_duplicates()

    for col in df.columns:

        # =========================
        # 🔢 STEP 1: TRY NUMERIC
        # =========================
        try:
            df[col] = pd.to_numeric(df[col], errors='raise')
            continue
        except:
            pass

        # =========================
        # 📅 STEP 2: TRY DATETIME (SMART)
        # =========================
        date_keywords = ["date", "time", "year", "month"]

        if any(word in col.lower() for word in date_keywords):
            converted = pd.to_datetime(df[col], errors='coerce')

            # Accept only if majority valid
            if converted.notna().sum() > len(df) * 0.6:
                df[col] = converted
                continue  # ✅ IMPORTANT (stop further processing)

        # =========================
        # 🔤 STEP 3: HANDLE STRINGS
        # =========================
        if df[col].dtype == "object":
            if df[col].mode().empty:
                df[col] = df[col].fillna("Unknown")
            else:
                df[col] = df[col].fillna(df[col].mode()[0])

        # =========================
        # 🔢 STEP 4: HANDLE NUMERIC (SAFE)
        # =========================
        elif pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].fillna(df[col].mean())

    return df
