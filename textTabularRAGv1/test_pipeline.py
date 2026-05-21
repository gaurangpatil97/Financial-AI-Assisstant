import json
import requests
from logger import logger

BASE_URL = "http://localhost:8000/api/v1/query"

# 40 Test Questions with Expected Answers
TEST_CASES = [
    # Annual-Report-2021-22
    {"question": "What was the company's Net Revenue in FY22?", "expected": "2,206 Crores", "source": "7.-Annual-Report-2021-22.pdf", "page": 15, "year": "2022"},
    {"question": "What was the Net Profit of the company in FY22?", "expected": "160 Crores", "source": "7.-Annual-Report-2021-22.pdf", "page": 15, "year": "2022"},
    {"question": "What was the Debt Equity Ratio in FY22?", "expected": "0.63", "source": "7.-Annual-Report-2021-22.pdf", "page": 15, "year": "2022"},
    {"question": "What was the EBITDA in FY22?", "expected": "539 Crores", "source": "7.-Annual-Report-2021-22.pdf", "page": 15, "year": "2022"},
    {"question": "What was the Networth of the company in FY22?", "expected": "1,142 Crores", "source": "7.-Annual-Report-2021-22.pdf", "page": 15, "year": "2022"},

    # Annual-Report-2025
    {"question": "What was the consolidated operating revenue for FY 2024-25?", "expected": "5,690.48 Crores", "source": "Annual-Report-2025.pdf", "page": 4, "year": "2025"},
    {"question": "What was the consolidated Profit After Tax for FY 2024-25?", "expected": "200.87 Crores", "source": "Annual-Report-2025.pdf", "page": 4, "year": "2025"},
    {"question": "What was the consolidated depreciation and amortization expense for FY 2024-25?", "expected": "347.02 Crores", "source": "Annual-Report-2025.pdf", "page": 4, "year": "2025"},
    {"question": "What final dividend was recommended for the financial year 2024-25?", "expected": "5 per Equity Share", "source": "Annual-Report-2025.pdf", "page": 5, "year": "2025"},
    {"question": "What was the foreign exchange outgo during FY 2024-25?", "expected": "703.30 Crores", "source": "Annual-Report-2025.pdf", "page": 14, "year": "2025"},

    # Craftsman-MGT-7-2025
    {"question": "What is the total turnover of Craftsman Automation as per MGT7 2025?", "expected": "38479436794", "source": "Craftsman-MGT-7-AB6987903-signed-2025.pdf", "page": 9, "year": "2025"},
    {"question": "What is the net worth of Craftsman Automation as per MGT7 2025?", "expected": "27439459488", "source": "Craftsman-MGT-7-AB6987903-signed-2025.pdf", "page": 9, "year": "2025"},
    {"question": "What percentage of turnover is from manufacture of motor vehicles trailers and semi trailers?", "expected": "74%", "source": "Craftsman-MGT-7-AB6987903-signed-2025.pdf", "page": 3, "year": "2025"},
    {"question": "What was the total remuneration paid to Managing Director Srinivasan Ravi as per MGT7 2025?", "expected": "59316923", "source": "Craftsman-MGT-7-AB6987903-signed-2025.pdf", "page": 16, "year": "2025"},
    {"question": "What was the eForm filing date of MGT7 2025?", "expected": "20/09/2025", "source": "Craftsman-MGT-7-AB6987903-signed-2025.pdf", "page": 20, "year": "2025"},

    # Annual-Report-2023-24
    {"question": "What was the consolidated revenue in FY24?", "expected": "4,452 Crore", "source": "Annual-Report-2023-24.pdf", "page": 16, "year": "2024"},
    {"question": "What was the consolidated Profit After Tax in FY24?", "expected": "337 Crore", "source": "Annual-Report-2023-24.pdf", "page": 16, "year": "2024"},
    {"question": "What was the standalone Networth in FY24?", "expected": "1,546 Crore", "source": "Annual-Report-2023-24.pdf", "page": 17, "year": "2024"},
    {"question": "What was the Debt Equity Ratio in FY24?", "expected": "0.88", "source": "Annual-Report-2023-24.pdf", "page": 19, "year": "2024"},
    {"question": "What was the EBITDA in FY24?", "expected": "897 Crore", "source": "Annual-Report-2023-24.pdf", "page": 16, "year": "2024"},

    # Annual-Report-2023
    {"question": "What was the company Revenue in FY23?", "expected": "2,980 crore", "source": "Annual-Report_2023.pdf", "page": 2, "year": "2023"},
    {"question": "What was the Profit After Tax in FY23?", "expected": "238 crore", "source": "Annual-Report_2023.pdf", "page": 2, "year": "2023"},
    {"question": "What was the Networth of the company in FY23?", "expected": "1,371 crore", "source": "Annual-Report_2023.pdf", "page": 2, "year": "2023"},
    {"question": "What was the Debt equity Ratio in FY23?", "expected": "0.72", "source": "Annual-Report_2023.pdf", "page": 19, "year": "2023"},
    {"question": "What was the EBITDA in FY23?", "expected": "671 crore", "source": "Annual-Report_2023.pdf", "page": 19, "year": "2023"},

    # MGT7-2023-24
    {"question": "What is the total turnover as per MGT7 2023-24?", "expected": "32,077,900,000", "source": "MGT7_8_2023-24_CRAFTSMAN_FINAL_CERTIFIED_27072024-1.pdf", "page": 8, "year": "2024"},
    {"question": "What is the net worth as per MGT7 2023-24?", "expected": "14,905,600,000", "source": "MGT7_8_2023-24_CRAFTSMAN_FINAL_CERTIFIED_27072024-1.pdf", "page": 8, "year": "2024"},
    {"question": "What percentage of turnover is from metal and metal products as per MGT7 2023-24?", "expected": "9.29%", "source": "MGT7_8_2023-24_CRAFTSMAN_FINAL_CERTIFIED_27072024-1.pdf", "page": 2, "year": "2024"},
    {"question": "What was the total remuneration paid to Srinivasan Ravi as per MGT7 2023-24?", "expected": "106,402,000", "source": "MGT7_8_2023-24_CRAFTSMAN_FINAL_CERTIFIED_27072024-1.pdf", "page": 13, "year": "2024"},
    {"question": "Were there any borrowings from directors or members during the year under review?", "expected": "No borrowings", "source": "MGT7_8_2023-24_CRAFTSMAN_FINAL_CERTIFIED_27072024-1.pdf", "page": 19, "year": "2024"},

    # Annual-Return-2023
    {"question": "What was the total turnover as per Annual Return 2023?", "expected": "29,802,400,000", "source": "Annual-Return.pdf", "page": 8, "year": "2023"},
    {"question": "What is the net worth as per Annual Return 2023?", "expected": "13,159,600,000", "source": "Annual-Return.pdf", "page": 8, "year": "2023"},
    {"question": "What is the total number of issued subscribed and paid up equity shares?", "expected": "21,128,311", "source": "Annual-Return.pdf", "page": 3, "year": "2023"},
    {"question": "What was the total remuneration paid to Srinivasan Ravi as per Annual Return 2023?", "expected": "134,635,000", "source": "Annual-Return.pdf", "page": 13, "year": "2023"},
    {"question": "Did the company have any unpaid or unclaimed dividends to transfer to IEPF?", "expected": "No", "source": "Annual-Return.pdf", "page": 19, "year": "2023"},

    # Annual-Return-2022
    {"question": "What percentage of turnover is from metal and metal products as per Annual Return 2022?", "expected": "10.3%", "source": "Annual-Return-2022.pdf", "page": 2, "year": "2022"},
    {"question": "What is the total number of subscribed equity shares as per Annual Return 2022?", "expected": "21,128,311", "source": "Annual-Return-2022.pdf", "page": 3, "year": "2022"},
    {"question": "What is the total nominal value of outstanding non convertible debentures as per Annual Return 2022?", "expected": "0", "source": "Annual-Return-2022.pdf", "page": 7, "year": "2022"},
    {"question": "What is the total number of shareholders other than promoters as per Annual Return 2022?", "expected": "60,135", "source": "Annual-Return-2022.pdf", "page": 9, "year": "2022"},
    {"question": "What was the total remuneration paid to Srinivasan Ravi as per Annual Return 2022?", "expected": "96,749,000", "source": "Annual-Return-2022.pdf", "page": 12, "year": "2022"},
]

def check_answer(answer: str, expected: str) -> bool:
    """Check if expected answer is contained in the response."""
    answer_lower = answer.lower()
    expected_lower = expected.lower()
    # Remove commas and spaces for number comparison
    answer_clean = answer_lower.replace(",", "").replace(" ", "")
    expected_clean = expected_lower.replace(",", "").replace(" ", "")
    return expected_clean in answer_clean

def check_citation(citations: list, expected_source: str, expected_page: int) -> bool:
    """Check if correct source and page appears in citations."""
    for citation in citations:
        if expected_source.lower() in citation["filename"].lower():
            if citation["page"] == expected_page:
                return True
    return False

def run_tests():
    results = []
    correct_answers = 0
    correct_citations = 0
    total = len(TEST_CASES)

    print(f"\n{'='*60}")
    print(f"Running {total} test cases...")
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

            status = "✅" if answer_correct else "❌"
            cite_status = "✅" if citation_correct else "❌"

            print(f"Q{i}: {test['question'][:60]}...")
            print(f"     Expected: {test['expected']}")
            print(f"     Answer: {status} | Citation: {cite_status}")
            if not answer_correct:
                print(f"     Got: {answer[:100]}...")
            print()

            results.append({
                "question": test["question"],
                "expected": test["expected"],
                "answer_correct": answer_correct,
                "citation_correct": citation_correct,
            })

        except Exception as e:
            print(f"Q{i}: ERROR — {e}")

    print(f"{'='*60}")
    print(f"RESULTS:")
    print(f"Answer Accuracy:   {correct_answers}/{total} = {correct_answers/total*100:.1f}%")
    print(f"Citation Accuracy: {correct_citations}/{total} = {correct_citations/total*100:.1f}%")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    run_tests()