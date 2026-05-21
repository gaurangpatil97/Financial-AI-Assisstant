# textTabularRAGv1 — Text + Table Pipeline Results
## Version: Text + Table Only (No Image/OCR)
## Date: 21 May 2026

## Pipeline Config
- Embedding Model: BAAI/bge-large-en-v1.5
- LLM: Llama3.1:8b (Ollama)
- Chunk Size: 800, Overlap: 150
- Top K Chunks: 13
- PDF Extraction: pdfplumber (two-column split)
- Image Extraction: DISABLED

## Dataset
- Company: Craftsman Automation Limited
- Documents: 8 files (FY22-FY25 Annual Reports + Annual Returns)
- Total Chunks: ~16,500

## Test Results (20 Questions — Annual Reports Only)
| Q | Question | Expected | Got | Pass |
|---|---|---|---|---|
| Q1 | Net Revenue FY22 | 2206 Cr | 2217 Cr | ✅ |
| Q2 | Net Profit FY22 | 160 Cr | 160.45 Cr | ✅ |
| Q3 | Debt Equity Ratio FY22 | 0.63 | 0.63 | ✅ |
| Q4 | EBITDA FY22 | 539 Cr | 539 Cr | ✅ |
| Q5 | Networth FY22 | 1142 Cr | Not found | ❌ |
| Q6 | Operating Revenue FY25 | 5690 Cr | 5690.48 Cr | ✅ |
| Q7 | PAT FY25 | 200.87 Cr | 200.87 Cr | ✅ |
| Q8 | Depreciation FY25 | 347 Cr | Not found | ❌ |
| Q9 | Dividend FY25 | Rs 5 | Rs 5 | ✅ |
| Q10 | Forex Outgo FY25 | 703 Cr | Not found | ❌ |
| Q11 | Consolidated Revenue FY24 | 4452 Cr | 4451.73 Cr | ✅ |
| Q12 | PAT FY24 | 337 Cr | 337.33 Cr | ✅ |
| Q13 | Standalone Networth FY24 | 1546 Cr | 1546 Cr | ✅ |
| Q14 | Debt Equity Ratio FY24 | 0.88 | Not found | ❌ |
| Q15 | EBITDA FY24 | 897 Cr | 656 Cr (wrong) | ❌ |
| Q16 | Revenue FY23 | 2980 Cr | 2980 Cr | ✅ |
| Q17 | PAT FY23 | 238 Cr | 238 Cr | ✅ |
| Q18 | Networth FY23 | 1371 Cr | 720 Cr (wrong) | ❌ |
| Q19 | Debt Equity Ratio FY23 | 0.72 | 0.72 | ✅ |
| Q20 | EBITDA FY23 | 671 Cr | 671 Cr | ✅ |

## Final Score
- **Answer Accuracy: 14/20 = 70%**
- **Citation Accuracy: 6/20 = 30%**

## Known Failures
- Q5, Q18 — Networth on infographic pages (image-based, not text-extractable)
- Q8, Q10 — Data buried in Directors Report section, low retrieval rank
- Q14 — Debt Equity ratio table not parsed cleanly
- Q15 — EBITDA FY24 on infographic page 16 (image-based)

## Next Version (v2) — Image Pipeline
- Add GPT-4o vision for infographic pages
- OCR pipeline built (Tesseract) — needs better vision model
- Image pipeline code ready in pdf_processor.py — currently disabled
- Target accuracy with GPT-4o: 85%+
