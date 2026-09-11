from pathlib import Path
from typing import Optional

from pypdf import PdfReader
import pymupdf

import pytesseract
from PIL import Image


# ============================================================
# WINDOWS TESSERACT CONFIGURATION
# ============================================================

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


# ============================================================
# PDF TEXT EXTRACTION
# ============================================================

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from a PDF.

    First tries normal PDF text extraction.
    If little/no text is found, OCR is used as a fallback.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    # --------------------------------------------------------
    # STEP 1: Normal PDF text extraction
    # --------------------------------------------------------

    reader = PdfReader(str(path))

    extracted_text = []

    for page in reader.pages:

        text = page.extract_text()

        if text:
            extracted_text.append(text)

    text = "\n".join(extracted_text).strip()

    # --------------------------------------------------------
    # STEP 2: Return extracted text if sufficient
    # --------------------------------------------------------

    if len(text) > 50:
        return text

    # --------------------------------------------------------
    # STEP 3: OCR fallback
    # --------------------------------------------------------

    ocr_text = []

    pdf = pymupdf.open(str(path))

    try:

        for page in pdf:

            # Render PDF page as image
            pix = page.get_pixmap(
                matrix=pymupdf.Matrix(2, 2)
            )

            # Convert image to PNG bytes
            image_bytes = pix.tobytes("png")

            import io

            image = Image.open(
                io.BytesIO(image_bytes)
            )

            # OCR
            page_text = pytesseract.image_to_string(
                image
            )

            if page_text:
                ocr_text.append(page_text)

    finally:
        pdf.close()

    return "\n".join(ocr_text).strip()


# ============================================================
# IMAGE TEXT EXTRACTION
# ============================================================

def extract_text_from_image(file_path: str) -> str:
    """
    Extract text from an image using Tesseract OCR.

    Supported image formats include:
        JPG
        JPEG
        PNG
        TIFF
        BMP
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Image file not found: {file_path}"
        )

    image = Image.open(path)

    text = pytesseract.image_to_string(image)

    return text.strip()


# ============================================================
# GENERIC DOCUMENT TEXT EXTRACTION
# ============================================================

def extract_text_from_document(
    file_path: str,
) -> str:
    """
    Extract text from a document based on its extension.

    Supported:
        PDF
        JPG
        JPEG
        PNG
        TIFF
        BMP

    Returns:
        Extracted text as a string.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Document not found: {file_path}"
        )

    extension = path.suffix.lower()

    # --------------------------------------------------------
    # PDF
    # --------------------------------------------------------

    if extension == ".pdf":

        return extract_text_from_pdf(
            str(path)
        )

    # --------------------------------------------------------
    # Image documents
    # --------------------------------------------------------

    image_extensions = {
        ".jpg",
        ".jpeg",
        ".png",
        ".tiff",
        ".tif",
        ".bmp",
    }

    if extension in image_extensions:

        return extract_text_from_image(
            str(path)
        )

    # --------------------------------------------------------
    # Unsupported format
    # --------------------------------------------------------

    raise ValueError(
        f"Unsupported document format: {extension}"
    )