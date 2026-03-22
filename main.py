from fastapi import FastAPI, UploadFile, File
import pandas as pd
import uuid
import os

from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# 🔥 your modules
from utils import clean_for_json
from cleaner import clean_data
from analyzer import analyze_data
from visualizer import create_visualizations
from llm import generate_plan, generate_code, explain_result
from executor import execute_code

# =========================
# APP SETUP
# =========================
app = FastAPI()

app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_STORE = {}

os.makedirs("uploads", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

def read_csv_safely(file_path):
    encodings = ["utf-8", "latin1", "cp1252"]

    for enc in encodings:
        try:
            return pd.read_csv(file_path, encoding=enc)
        except:
            continue

    raise ValueError("Could not read CSV with supported encodings")
# =========================
# UPLOAD
# =========================
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_id = str(uuid.uuid4())
    file_path = f"uploads/{file_id}.csv"

    with open(file_path, "wb") as f:
        f.write(await file.read())

    df = read_csv_safely(file_path)
    # ✅ CLEAN
    df = clean_data(df)

    # ✅ ANALYZE
    summary = analyze_data(df)

    # ✅ VISUALIZE
    charts = create_visualizations(df, summary, file_id)

    # ✅ STORE
    DATA_STORE[file_id] = df

    return {
        "file_id": file_id,
        "summary": clean_for_json(summary),
        "charts": charts
    }

# =========================
# ASK AI
# =========================
@app.post("/ask")
async def ask_question(file_id: str, question: str):
    if file_id not in DATA_STORE:
        return {"error": "Invalid file_id"}

    df = DATA_STORE[file_id]

    # 🧠 PLAN
    plan = generate_plan(question)

    # ⚙️ CODE
    code = generate_code(question, plan, df.columns.tolist())

    # ⚙️ EXECUTE
    execution = execute_code(code, df)

    output = execution.get("output", "")
    chart = execution.get("chart", None)

    # 🔍 EXPLAIN
    explanation = explain_result(question, str(output))

    return {
        "question": question,
        "result": {
            "output": str(output),
            "chart": chart
        },
        "explanation": explanation
    }

# =========================
# KPI
# =========================
@app.get("/kpi")
def get_kpis(file_id: str):
    if file_id not in DATA_STORE:
        return {"error": "Invalid file_id"}

    df = DATA_STORE[file_id]

    total_revenue = df["Total Revenue"].sum()
    total_profit = df["Total Profit"].sum()
    total_units = df["Units Sold"].sum()

    avg_margin = (total_profit / total_revenue) * 100 if total_revenue != 0 else 0

    return {
        "total_revenue": round(total_revenue, 2),
        "total_profit": round(total_profit, 2),
        "total_units": int(total_units),
        "avg_margin": round(avg_margin, 2)
    }