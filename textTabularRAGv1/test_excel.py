import json
import re
from pathlib import Path

import requests

BASE_URL = "http://localhost:8000/api/v1/query"
RESULTS_DIR = Path("results")
RESULTS_PATH = RESULTS_DIR / "exp1_excel_results.md"

QUESTIONS = [
    {"question": "What was the total sales revenue for FY2025?", "expected": "5690.48", "year": "2025", "section": "P&L"},
    {"question": "What was the net profit for FY2025?", "expected": "194.57", "year": "2025", "section": "P&L"},
    {"question": "What was the depreciation expense for FY2025?", "expected": "347.02", "year": "2025", "section": "P&L"},
    {"question": "What was the EBITDA for FY2025?", "expected": "833.31", "year": "2025", "section": "P&L"},
    {"question": "What was the total sales revenue for FY2024?", "expected": "4451.73", "year": "2024", "section": "P&L"},
    {"question": "What was the net profit for FY2024?", "expected": "304.47", "year": "2024", "section": "P&L"},
    {"question": "What was the depreciation for FY2024?", "expected": "277.69", "year": "2024", "section": "P&L"},
    {"question": "What was the total sales revenue for FY2023?", "expected": "3182.6", "year": "2023", "section": "P&L"},
    {"question": "What was the net profit for FY2023?", "expected": "248.39", "year": "2023", "section": "P&L"},
    {"question": "What were the total borrowings for FY2025?", "expected": "2358.18", "year": "2025", "section": "Balance Sheet"},
    {"question": "What was the networth for FY2025?", "expected": "2856.74", "year": "2025", "section": "Balance Sheet"},
    {"question": "What were the reserves for FY2024?", "expected": "1647.42", "year": "2024", "section": "Balance Sheet"},
    {"question": "What was cash from operating activity for FY2025?", "expected": "283.33", "year": "2025", "section": "Cash Flow"},
    {"question": "What was cash from operating activity for FY2024?", "expected": "513.31", "year": "2024", "section": "Cash Flow"},
    {"question": "What was the net cash flow for FY2023?", "expected": "-2.11", "year": "2023", "section": "Cash Flow"},
]


# Additional derived and cross-section questions (Q16-Q30)
QUESTIONS += [
    {"question": "What was the interest coverage ratio for FY2025?", "expected": "3.85", "year": "2025", "section": "Derived"},
    {"question": "What was the debt to equity ratio for FY2025?", "expected": "0.83", "year": "2025", "section": "Derived"},
    {"question": "What was the debt to equity ratio for FY2024?", "expected": "1.06", "year": "2024", "section": "Derived"},
    {"question": "What was the debt to equity ratio for FY2023?", "expected": "0.90", "year": "2023", "section": "Derived"},
    {"question": "What was the return on equity for FY2025?", "expected": "6.81", "year": "2025", "section": "Derived"},
    {"question": "What was the return on equity for FY2024?", "expected": "18.36", "year": "2024", "section": "Derived"},
    {"question": "What was the interest as percentage of sales for FY2025?", "expected": "3.81", "year": "2025", "section": "Derived"},
    {"question": "What was the net profit margin for FY2025?", "expected": "3.42", "year": "2025", "section": "Derived"},
    {"question": "What was the net profit margin for FY2024?", "expected": "6.84", "year": "2024", "section": "Derived"},
    {"question": "What was the net profit margin for FY2023?", "expected": "7.80", "year": "2023", "section": "Derived"},
    {"question": "What was the cash conversion ratio for FY2025?", "expected": "1.46", "year": "2025", "section": "Cross"},
    {"question": "What was the cash conversion ratio for FY2024?", "expected": "1.69", "year": "2024", "section": "Cross"},
    {"question": "What was the cash conversion ratio for FY2023?", "expected": "2.45", "year": "2023", "section": "Cross"},
    {"question": "By how much did sales grow from FY2023 to FY2025?", "expected": "2507.88", "year": "2025", "section": "Trend"},
    {"question": "By how much did net profit change from FY2024 to FY2025?", "expected": "-109.90", "year": "2025", "section": "Trend"},
]


def extract_numbers(text: str) -> list[float]:
    # Supports signed numbers and decimal values, strips comma separators first.
    cleaned = text.replace(",", "")
    matches = re.findall(r"[-+]?\d*\.?\d+", cleaned)
    values = []
    for m in matches:
        try:
            values.append(float(m))
        except ValueError:
            continue
    return values


def check_expected_in_answer(answer: str, expected: str) -> tuple[bool, str]:
    numbers = extract_numbers(answer)

    try:
        expected_value = float(expected)
    except ValueError:
        return False, "Expected value is not numeric"

    # If expected is a small ratio (<1), use an absolute tolerance of 0.01
    # Otherwise use a relative tolerance of 1%.
    if expected_value == 0:
        tolerance = 0.0
    elif abs(expected_value) < 1.0:
        tolerance = 0.01
    else:
        tolerance = abs(expected_value) * 0.01

    for num in numbers:
        # If the answer was given with a % sign or as 'percent', extract_numbers
        # already yields the numeric portion. Comparison applies the same.
        if abs(num - expected_value) <= tolerance:
            return True, str(num)

    return False, str(numbers[:10]) if numbers else "No numeric values found"


def format_citations(citations: object) -> str:
    if not isinstance(citations, list):
        return "[]"
    try:
        return json.dumps(citations, ensure_ascii=True)
    except Exception:
        return str(citations)


def call_api(question: str, year: str) -> dict:
    payload = {
        "question": question,
        "year": year,
    }
    response = requests.post(BASE_URL, json=payload, timeout=120)
    response.raise_for_status()
    return response.json()


def run_tests() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    results = []
    passed = 0
    total = len(QUESTIONS)

    print("=" * 72)
    print(f"Running Exp1 Excel tests: {total} questions")
    print("=" * 72)

    for i, item in enumerate(QUESTIONS, start=1):
        question = item["question"]
        expected = item["expected"]
        year = item["year"]
        section = item["section"]

        try:
            data = call_api(question, year)
            answer = data.get("answer", "")
            citations = data.get("citations", [])

            is_pass, got_value = check_expected_in_answer(answer, expected)
            if is_pass:
                passed += 1

            status = "PASS" if is_pass else "FAIL"
            print(f"Q{i:02d} [{section}] - {status}")
            print(f"  Question: {question}")
            print(f"  Expected: {expected} | Got: {got_value}")

            results.append(
                {
                    "index": i,
                    "question": question,
                    "expected": expected,
                    "year": year,
                    "section": section,
                    "answer": answer,
                    "citations": citations,
                    "got": got_value,
                    "pass": is_pass,
                }
            )
        except Exception as exc:
            print(f"Q{i:02d} [{section}] - ERROR")
            print(f"  Question: {question}")
            print(f"  Error: {exc}")

            results.append(
                {
                    "index": i,
                    "question": question,
                    "expected": expected,
                    "year": year,
                    "section": section,
                    "answer": f"ERROR: {exc}",
                    "citations": [],
                    "got": "error",
                    "pass": False,
                }
            )

    lines = []
    lines.append("# Exp1 Excel Only Results")
    lines.append(f"## Summary: {passed}/{total} passed")
    lines.append("")
    lines.append("| Q# | Question | Expected | Got | Pass/Fail |")
    lines.append("|---|---|---|---|---|")

    for r in results:
        status = "PASS" if r["pass"] else "FAIL"
        q = r["question"].replace("|", "\\|")
        expected = str(r["expected"]).replace("|", "\\|")
        got = str(r["got"]).replace("|", "\\|")
        lines.append(f"| Q{r['index']} | {q} | {expected} | {got} | {status} |")

    lines.append("")
    lines.append("## Full Answers")

    for r in results:
        status = "PASS" if r["pass"] else "FAIL"
        lines.append("")
        lines.append(f"### Q{r['index']}")
        lines.append(f"**Question:** {r['question']}")
        lines.append(f"**Expected:** {r['expected']}")
        lines.append(f"**RAG Answer:** {r['answer']}")
        lines.append(f"**Citations:** {format_citations(r['citations'])}")
        lines.append(f"**Result:** {status}")

    RESULTS_PATH.write_text("\n".join(lines), encoding="utf-8")

    print("=" * 72)
    print(f"Done. Summary: {passed}/{total} passed")
    print(f"Results written to: {RESULTS_PATH}")
    print("=" * 72)


if __name__ == "__main__":
    run_tests()
