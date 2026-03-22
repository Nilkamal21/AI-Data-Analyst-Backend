import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os

OUTPUT_DIR = "outputs"


# =========================
# 🎨 PROFESSIONAL STYLE
# =========================
def apply_professional_style(fig):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0B0F19",
        plot_bgcolor="#0B0F19",
        font=dict(color="#E5E7EB", size=14),
        margin=dict(l=40, r=40, t=50, b=40),
        title=dict(x=0.5, font=dict(size=18)),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
    )
    return fig


# =========================
# 🧠 SMART COLUMN SELECTION
# =========================
def smart_column_selection(df, summary):
    numeric_cols = summary["numeric_columns"]
    categorical_cols = summary["categorical_columns"]
    datetime_cols = summary["datetime_columns"]

    # Remove useless numeric columns
    numeric_cols = [
        col for col in numeric_cols
        if df[col].nunique() > 5 and "id" not in col.lower()
    ]

    # Clean categorical
    categorical_cols = [
        col for col in categorical_cols
        if 2 < df[col].nunique() < 50
    ]

    # Best numeric (highest variance)
    best_numeric = max(numeric_cols, key=lambda col: df[col].std()) if numeric_cols else None

    # Second numeric (for scatter)
    second_numeric = None
    if len(numeric_cols) > 1:
        sorted_nums = sorted(numeric_cols, key=lambda col: df[col].std(), reverse=True)
        second_numeric = sorted_nums[1]

    # Best categorical
    best_categorical = None
    if categorical_cols:
        best_categorical = max(
            categorical_cols,
            key=lambda col: df.groupby(col).size().std()
        )

    # Second categorical
    second_categorical = categorical_cols[1] if len(categorical_cols) > 1 else None

    # Best date
    best_date = datetime_cols[0] if datetime_cols else None

    return best_numeric, second_numeric, best_categorical, second_categorical, best_date


# =========================
# 📊 MAIN VISUALIZATION ENGINE
# =========================
def create_visualizations(df, summary, file_id):
    paths = []

    best_num, second_num, best_cat, second_cat, best_date = smart_column_selection(df, summary)

    # =========================
    # 🔥 1. MAIN INSIGHT (TOP CATEGORY)
    # =========================
    if best_cat and best_num:
        data = (
            df.groupby(best_cat)[best_num]
            .sum()
            .sort_values(ascending=False)
            .head(5)
            .reset_index()
        )

        fig = px.bar(
            data,
            x=best_num,
            y=best_cat,
            orientation="h",
            text=data[best_num].round(0),
            color=best_num,
            color_continuous_scale="Blues"
        )

        fig.update_traces(textposition="outside")

        fig.update_layout(
            title=f"Top {best_cat} by {best_num}",
            coloraxis_showscale=False
        )

        fig = apply_professional_style(fig)

        path = f"{OUTPUT_DIR}/{file_id}_main.html"
        fig.write_html(path)
        paths.append(path)

    # =========================
    # 🔥 2. DISTRIBUTION
    # =========================
    if best_num:
        fig = px.histogram(
            df,
            x=best_num,
            nbins=25,
            color_discrete_sequence=["#3B82F6"]
        )

        fig.update_layout(
            title=f"{best_num} Distribution",
            showlegend=False
        )

        fig = apply_professional_style(fig)

        path = f"{OUTPUT_DIR}/{file_id}_dist.html"
        fig.write_html(path)
        paths.append(path)

    # =========================
    # 🔥 3. TIME SERIES
    # =========================
    if best_date and best_num:
        df[best_date] = pd.to_datetime(df[best_date], errors="coerce")

        trend = (
            df.groupby(best_date)[best_num]
            .sum()
            .reset_index()
        )

        fig = px.line(
            trend,
            x=best_date,
            y=best_num,
            markers=True
        )

        fig.update_traces(
            line=dict(width=3, color="#22C55E")
        )

        fig.update_layout(title=f"{best_num} Over Time")

        fig = apply_professional_style(fig)

        path = f"{OUTPUT_DIR}/{file_id}_trend.html"
        fig.write_html(path)
        paths.append(path)

    # =========================
    # 🔥 4. SECOND INSIGHT (SMART)
    # =========================
    # Prefer scatter if 2 numeric exist
    if best_num and second_num:
        fig = px.scatter(
            df,
            x=best_num,
            y=second_num,
            opacity=0.7
        )

        fig.update_layout(
            title=f"{best_num} vs {second_num}"
        )

        fig = apply_professional_style(fig)

        path = f"{OUTPUT_DIR}/{file_id}_scatter.html"
        fig.write_html(path)
        paths.append(path)

    # fallback → second categorical
    elif second_cat:
        data = df[second_cat].value_counts().head(5).reset_index()
        data.columns = [second_cat, "Count"]

        fig = px.bar(
            data,
            x="Count",
            y=second_cat,
            orientation="h",
            text="Count",
            color="Count",
            color_continuous_scale="Purples"
        )

        fig.update_traces(textposition="outside")

        fig.update_layout(
            title=f"Top {second_cat}",
            coloraxis_showscale=False
        )

        fig = apply_professional_style(fig)

        path = f"{OUTPUT_DIR}/{file_id}_secondary.html"
        fig.write_html(path)
        paths.append(path)

    # =========================
    # 🎯 FINAL OUTPUT (ALWAYS 4)
    # =========================
    return paths[:4]