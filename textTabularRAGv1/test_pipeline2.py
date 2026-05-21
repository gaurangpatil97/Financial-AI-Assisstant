import requests
import re

BASE_URL = "http://localhost:8000/api/v1/query"

TEST_CASES = [
    # Annual-Report-2021-22
    {"question": "What was the company's Net Revenue in FY22?", "expected": "2206", "source": "7.-Annual-Report-2021-22.pdf", "page": 15, "year": "2022"},
    {"question": "What was the Net Profit of the company in FY22?", "expected": "160", "source": "7.-Annual-Report-2021-22.pdf", "page": 15, "year": "2022"},
    {"question": "What was the Debt Equity Ratio in FY22?", "expected": "063", "source": "7.-Annual-Report-2021-22.pdf", "page": 15, "year": "2022"},
    {"question": "What was the EBITDA in FY22?", "expected": "539", "source": "7.-Annual-Report-2021-22.pdf", "page": 15, "year": "2022"},
    {"question": "What was the Networth of the company in FY22?", "expected": "1142", "source": "7.-Annual-Report-2021-22.pdf", "page": 15, "year": "2022"},

    # Annual-Report-2025
    {"question": "What was the consolidated operating revenue for FY 2024-25?", "expected": "569048", "source": "Annual-Report-2025.pdf", "page": 4, "year": "2025"},
    {"question": "What was the consolidated Profit After Tax for FY 2024-25?", "expected": "20087", "source": "Annual-Report-2025.pdf", "page": 4, "year": "2025"},
    {"question": "What was the consolidated depreciation and amortization expense for FY 2024-25?", "expected": "34702", "source": "Annual-Report-2025.pdf", "page": 4, "year": "2025"},
    {"question": "What final dividend was recommended for the financial year 2024-25?", "expected": "5", "source": "Annual-Report-2025.pdf", "page": 5, "year": "2025"},
    {"question": "What was the foreign exchange outgo during FY 2024-25?", "expected": "70330", "source": "Annual-Report-2025.pdf", "page": 14, "year": "2025"},

    # Annual-Report-2023-24
    {"question": "What was the consolidated revenue in FY24?", "expected": "4452", "source": "Annual-Report-2023-24.pdf", "page": 16, "year": "2024"},
    {"question": "What was the consolidated Profit After Tax in FY24?", "expected": "337", "source": "Annual-Report-2023-24.pdf", "page": 16, "year": "2024"},
    {"question": "What was the standalone Networth in FY24?", "expected": "1546", "source": "Annual-Report-2023-24.pdf", "page": 17, "year": "2024"},
    {"question": "What was the Debt Equity Ratio in FY24?", "expected": "088", "source": "Annual-Report-2023-24.pdf", "page": 19, "year": "2024"},
    {"question": "What was the EBITDA in FY24?", "expected": "897", "source": "Annual-Report-2023-24.pdf", "page": 16, "year": "2024"},

    # Annual-Report-2023
    {"question": "What was the company Revenue in FY23?", "expected": "2980", "source": "Annual-Report_2023.pdf", "page": 2, "year": "2023"},
    {"question": "What was the Profit After Tax in FY23?", "expected": "238", "source": "Annual-Report_2023.pdf", "page": 2, "year": "2023"},
    {"question": "What was the Networth of the company in FY23?", "expected": "1371", "source": "Annual-Report_2023.pdf", "page": 2, "year": "2023"},
    {"question": "What was the Debt equity Ratio in FY23?", "expected": "072", "source": "Annual-Report_2023.pdf", "page": 19, "year": "2023"},
    {"question": "What was the EBITDA in FY23?", "expected": "671", "source": "Annual-Report_2023.pdf", "page": 19, "year": "2023"},
]

def clean(s: str) -> str:
    return (
        s.lower()
        .replace(",", "")
        .replace(" ", "")
        .replace("₹", "")
        .replace("c", "")
        .replace("d", "")
        .replace(".", "")
        .replace("crore", "")
        .replace("crores", "")
        .replace("lakh", "")
        .replace("lakhs", "")
        .replace("rupees", "")
        .replace("%", "")
        .replace("x", "")
        .replace("(", "")
        .replace(")", "")
        .replace("-", "")
        .replace("/", "")
    )

def check_answer(answer: str, expected: str) -> bool:
    if clean(expected) in clean(answer):
        return True

    expected_nums = re.findall(r'\d+', clean(expected))
    answer_nums = re.findall(r'\d+', clean(answer))

    if not expected_nums:
        return False

    expected_num = int(expected_nums[0])

    for num in answer_nums:
        try:
            n = int(num)
            if n == expected_num:
                return True
            if abs(n - expected_num) <= 2:
                return True
            if n == expected_num * 100:
                return True
            if expected_num == n * 100:
                return True
        except:
            pass

    return False

def check_citation(citations: list, expected_source: str, expected_page: int) -> bool:
    for citation in citations:
        if expected_source.lower() in citation["filename"].lower():
            if citation["page"] == expected_page:
                return True
    return False

def run_tests():
    correct_answers = 0
    correct_citations = 0
    total = len(TEST_CASES)

    print(f"\n{'='*60}")
    print(f"Running {total} Annual Report test cases...")
    print(f"{'='*60}\n")

    for i, test in enumerate(TEST_CASES, 1):
        try:
            response = requests.post(
                BASE_URL,
                json={
                    "question": test["question"],
                    "year": test["year"]
                }
            )
            data = response.json()
            answer = data.get("answer", "")
            citations = data.get("citations", [])

            answer_correct = check_answer(answer, test["expected"])
            citation_correct = check_citation(citations, test["source"], test["page"])

            if answer_correct:
                correct_answers += 1
            if citation_correct:
                correct_citations += 1

            status = "PASS" if answer_correct else "FAIL"
            cite_status = "PASS" if citation_correct else "FAIL"

            print(f"{'='*60}")
            print(f"Q{i}: {test['question']}")
            print(f"Expected: {test['expected']}")
            print(f"Auto Score — Answer: {status} | Citation: {cite_status}")
            print(f"Expected Source: {test['source']} (Page {test['page']})")
            print(f"\nFULL ANSWER FROM RAG:")
            print(f"{answer}")
            print(f"\nCITATIONS:")
            for c in citations:
                print(f"  - {c['filename']} (Page {c['page']})")
            print()

        except Exception as e:
            print(f"Q{i}: ERROR — {e}")

    print(f"{'='*60}")
    print(f"AUTO SCORE RESULTS:")
    print(f"Answer Accuracy:   {correct_answers}/{total} = {correct_answers/total*100:.1f}%")
    print(f"Citation Accuracy: {correct_citations}/{total} = {correct_citations/total*100:.1f}%")
    print(f"{'='*60}")
    print(f"\nNow manually review each answer above and count your real score.")

if __name__ == "__main__":
    run_tests()