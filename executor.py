import io
import sys
import os

def execute_code(code, df):
    local_vars = {"df": df}

    # Delete any stale chart from a previous query so it won't bleed into this result
    chart_path = "outputs/chart.html"
    if os.path.exists(chart_path):
        os.remove(chart_path)

    old_stdout = sys.stdout
    sys.stdout = buffer = io.StringIO()

    try:
        exec(code, {}, local_vars)

        output = buffer.getvalue()  # CAPTURE PRINT OUTPUT

        sys.stdout = old_stdout

        return {
            "output": output.strip(),
            "chart": chart_path if os.path.exists(chart_path) else None
        }

    except Exception as e:
        sys.stdout = old_stdout
        return {"error": str(e)}