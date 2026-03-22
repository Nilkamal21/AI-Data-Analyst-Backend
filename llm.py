import cohere
import re

import os
import cohere
from dotenv import load_dotenv

load_dotenv()

co = cohere.Client(os.getenv("COHERE_API_KEY"))
# =========================
# CLEAN CODE
# =========================
def clean_code(code: str) -> str:
    code = re.sub(r"```.*?\n", "", code)
    code = code.replace("```", "")
    return code.strip()


# =========================
# 🧠 PLAN
# =========================
def generate_plan(question: str) -> str:
    prompt = f"""
Break the user question into 2-3 simple steps.

Question:
{question}
"""
    response = co.chat(
        model="command-a-03-2025",
        message=prompt,
        temperature=0.3
    )
    return response.text.strip()


# =========================
# ⚙️ CODE GENERATION (FIXED)
# =========================
def generate_code(question: str, plan: str, columns: list) -> str:
    prompt = f"""
You are a senior Python data analyst and visualization expert.

DataFrame name: df
Columns: {columns}

User Question:
{question}

Plan:
{plan}

========================
CORE RULES
========================

1. ALWAYS use df
2. NEVER guess values
3. NEVER say "no data available"
4. ALWAYS compute using pandas
5. ALWAYS print final result

========================
DATA LOGIC
========================

- Profit Margin:
    df['profit_margin'] = (df['Total Profit'] / df['Total Revenue']) * 100

- Time Series:
    Use 'Order Date' if available

- Grouping:
    Use groupby() when needed

- Sorting:
    Always sort values before output

========================
SMART DECISION (VERY IMPORTANT)
========================

IF question contains:
["which", "highest", "lowest", "average", "value"]

→ DO NOT CREATE ANY CHART  
→ ONLY compute and print result  

ELSE IF question contains:
["top", "trend", "distribution", "compare", "chart", "correlation"]

→ CREATE CHART  

========================
CHART SELECTION (AUTO)
========================

- Comparison → bar chart
- Many categories (>5) → horizontal bar
- Time-based → line chart with markers
- Distribution → histogram
- Relationship → scatter
- Correlation → heatmap

========================
VISUAL DESIGN (VERY IMPORTANT)
========================

- Use plotly.express (px)
- Use dark theme: template="plotly_dark"
- Use colors: ["#6366F1", "#8B5CF6", "#06B6D4"]
- Add text labels (text_auto=True for bar)
- Add markers for line chart
- Center title
- Clean layout

========================
SMART FILTERING
========================

- If many categories → limit to top 5
- If user says "top N" → use N
- If "least" → sort ascending

========================
OUTPUT RULES
========================

- Always print result
- If chart → save as outputs/chart.html
- DO NOT explain anything
- DO NOT return markdown
- Return ONLY Python code

========================
EXAMPLES
========================

Top 5 countries:
df.groupby('Country')['Total Revenue'].sum().sort_values(ascending=False).head(5)

Trend:
df.groupby('Order Date')['Total Revenue'].sum()

========================
NOW GENERATE CODE
========================
"""

    response = co.chat(
        model="command-a-03-2025",
        message=prompt,
        temperature=0.2
    )

    return clean_code(response.text.strip())

# =========================
# 🔍 EXPLANATION (FIXED)
# =========================
def explain_result(question: str, output: str) -> str:
    prompt = f"""
You are a data analyst.

User Question:
{question}

Actual Computed Result:
{output}

STRICT RULES:

- ONLY use given result
- NO external knowledge
- NO assumptions
- NO theory

FORMAT:

- If list/table → summarize top values
- If single value → direct answer

Keep it SHORT (1–2 lines)

Examples:

Result:
Honduras 6336545
Myanmar 6100000

Answer:
Honduras has the highest revenue, followed by Myanmar.

Result:
36.21

Answer:
The average profit margin is 36.21%.

Now answer:
"""

    response = co.chat(
        model="command-a-03-2025",
        message=prompt
    )

    return response.text.strip()