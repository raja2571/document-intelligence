from pathlib import Path

from pypdf import PdfReader
import pytesseract
from PIL import Image
import pymupdf


# Windows: Tesseract installation path
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from a PDF.

    First tries normal PDF text extraction.
    If little/no text is found, uses OCR with Tesseract.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"PDF file not found: {file_path}"
        )

    # --------------------------------------------------
    # STEP 1: Try normal PDF text extraction
    # --------------------------------------------------

    reader = PdfReader(str(path))

    extracted_text = []

    for page in reader.pages:
        text = page.extract_text()

        if text:
            extracted_text.append(text)

    text = "\n".join(extracted_text).strip()

    # If enough text was extracted, return it
    if len(text) > 50:
        return text

    # --------------------------------------------------
    # STEP 2: OCR fallback
    # --------------------------------------------------

    ocr_text = []

    pdf = pymupdf.open(str(path))

    for page in pdf:

        # Render PDF page as an image
        pix = page.get_pixmap(matrix=pymupdf.Matrix(2, 2))

        # Convert Pixmap to bytes
        image_bytes = pix.tobytes("png")

        # Open bytes as PIL image
        import io

        image = Image.open(io.BytesIO(image_bytes))

        # OCR
        page_text = pytesseract.image_to_string(image)

        if page_text:
            ocr_text.append(page_text)

    pdf.close()

    return "\n".join(ocr_text).strip()