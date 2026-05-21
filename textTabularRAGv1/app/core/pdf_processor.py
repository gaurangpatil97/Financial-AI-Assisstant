import os
import pdfplumber
import fitz
from pathlib import Path
import pytesseract
from PIL import Image
from logger import logger

pytesseract.pytesseract.tesseract_cmd = r'D:\ocr_setup\tesseract.exe'
os.environ['TESSDATA_PREFIX'] = r'D:\ocr_setup\tessdata'

def extract_pdf(file_path: str) -> list[dict]:
    """
    Existing text extraction — unchanged.
    Extracts text using two-column split.
    """
    file_path = Path(file_path)
    filename = file_path.name
    pages_data = []

    logger.info(f"Processing PDF (text): {filename}")

    with pdfplumber.open(file_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            width = page.width
            left = page.within_bbox((0, 0, width/2, page.height))
            right = page.within_bbox((width/2, 0, width, page.height))
            left_text = left.extract_text() or ""
            right_text = right.extract_text() or ""
            text = left_text + "\n" + right_text

            if text.strip():
                pages_data.append({
                    "content": text.strip(),
                    "metadata": {
                        "filename": filename,
                        "page": page_num,
                        "source": str(file_path),
                        "chunk_type": "text"
                    }
                })

    logger.success(f"Extracted {len(pages_data)} pages from {filename}")
    return pages_data


def describe_image(image_path: str, page_num: int) -> str:
    """Extract text from image using Tesseract OCR."""
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img, config='--psm 6')
        text = text.strip()
        if len(text) < 20:
            return ""
        logger.info(f"OCR extracted {len(text)} chars from page {page_num}")
        return text
    except Exception as e:
        logger.error(f"OCR failed on page {page_num}: {e}")
        return ""


def extract_images_from_pdf(file_path: str) -> list[dict]:
    """
    Renders pages with images to PNG at 200 DPI and sends to GPT-4o mini.
    """
    file_path = Path(file_path)
    filename = file_path.name
    pages_data = []
    tmp_dir = "D:/financial_rag/tmp_images"
    os.makedirs(tmp_dir, exist_ok=True)

    logger.info(f"Processing PDF (images): {filename}")

    doc_fitz = fitz.open(str(file_path))

    for page_num in range(len(doc_fitz)):
        page_fitz = doc_fitz[page_num]
        page_display_num = page_num + 1
        images = page_fitz.get_images()

        if not images:
            continue

        try:
            matrix = fitz.Matrix(200 / 72, 200 / 72)
            pix = page_fitz.get_pixmap(matrix=matrix)

            if pix.colorspace and pix.colorspace != fitz.csRGB:
                pix = fitz.Pixmap(fitz.csRGB, pix)

            img_path = f"{tmp_dir}/page_{page_display_num}.png"
            pix.save(img_path)

            description = describe_image(img_path, page_display_num)

            try:
                os.remove(img_path)
            except:
                pass

            if description:
                pages_data.append({
                    "content": f"[IMAGE CONTENT - Page {page_display_num}]\n{description}",
                    "metadata": {
                        "filename": filename,
                        "page": page_display_num,
                        "source": str(file_path),
                        "chunk_type": "image"
                    }
                })
        except Exception as e:
            logger.error(f"Failed to render page {page_display_num}: {e}")
            continue

    doc_fitz.close()
    logger.success(f"Extracted image descriptions from {len(pages_data)} pages in {filename}")
    return pages_data