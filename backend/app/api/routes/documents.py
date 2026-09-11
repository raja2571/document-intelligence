import json
import uuid
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session

from backend.app.core.database import SessionLocal
from backend.app.models.document import Document

from backend.app.services.document_extractor import (
    extract_text_from_document,
)

from backend.app.services.document_classifier import (
    classify_document,
)

from backend.app.services.field_extractor import (
    extract_financial_fields,
)


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/api/v1/documents",
    tags=["Documents"],
)


# ============================================================
# CONFIGURATION
# ============================================================

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".jpg",
    ".jpeg",
    ".png",
}

ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
}


# ============================================================
# DATABASE DEPENDENCY
# ============================================================

def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# ============================================================
# HELPER
# ============================================================

def normalize_extracted_fields(extracted_fields):
    """
    Make sure extracted_fields is returned as a Python dictionary.

    New records stored using SQLAlchemy JSON will already be a dict.

    This also handles older records where extracted_fields
    may have been stored as a JSON string.
    """

    if not extracted_fields:
        return {}

    if isinstance(extracted_fields, dict):
        return extracted_fields

    if isinstance(extracted_fields, str):

        try:
            return json.loads(extracted_fields)

        except json.JSONDecodeError:
            return {}

    return {}


# ============================================================
# UPLOAD DOCUMENT
# ============================================================

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):

    # --------------------------------------------------------
    # 1. Check filename
    # --------------------------------------------------------

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="Filename is required.",
        )

    # --------------------------------------------------------
    # 2. Get file extension
    # --------------------------------------------------------

    file_extension = Path(
        file.filename
    ).suffix.lower()

    # --------------------------------------------------------
    # 3. Check file extension
    # --------------------------------------------------------

    if file_extension not in ALLOWED_EXTENSIONS:

        raise HTTPException(
            status_code=400,
            detail=(
                "Only PDF, JPG, JPEG, and PNG "
                "files are allowed."
            ),
        )

    # --------------------------------------------------------
    # 4. Check MIME type
    # --------------------------------------------------------

    if file.content_type not in ALLOWED_CONTENT_TYPES:

        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid file type. "
                "Only PDF, JPG, JPEG, and PNG "
                "files are allowed."
            ),
        )

    # --------------------------------------------------------
    # 5. Read file
    # --------------------------------------------------------

    contents = await file.read()

    # --------------------------------------------------------
    # 6. Check empty file
    # --------------------------------------------------------

    if not contents:

        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty.",
        )

    # --------------------------------------------------------
    # 7. Check file size
    # --------------------------------------------------------

    if len(contents) > MAX_FILE_SIZE:

        raise HTTPException(
            status_code=400,
            detail="File size must be less than 10 MB.",
        )

    # --------------------------------------------------------
    # 8. Generate unique document ID
    # --------------------------------------------------------

    document_id = str(uuid.uuid4())

    # --------------------------------------------------------
    # 9. Create file path
    # --------------------------------------------------------

    file_path = (
        UPLOAD_DIR
        / f"{document_id}{file_extension}"
    )

    # --------------------------------------------------------
    # 10. Save uploaded file
    # --------------------------------------------------------

    try:

        file_path.write_bytes(contents)

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Failed to save file: {str(e)}",
        )

    # --------------------------------------------------------
    # 11. Create database record
    # --------------------------------------------------------

    document = Document(
        document_id=document_id,
        filename=file.filename,
        file_path=str(file_path),
        status="processing",
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    # --------------------------------------------------------
    # 12. Extract text
    # --------------------------------------------------------

    try:

        extracted_text = extract_text_from_document(
            str(file_path)
        )

    except Exception as e:

        document.status = "failed"

        db.commit()

        raise HTTPException(
            status_code=500,
            detail=(
                f"Text extraction failed: {str(e)}"
            ),
        )

    # --------------------------------------------------------
    # 13. Check extracted text
    # --------------------------------------------------------

    if not extracted_text:

        document.status = "failed"

        db.commit()

        raise HTTPException(
            status_code=422,
            detail=(
                "Could not extract text "
                "from the document."
            ),
        )

    # --------------------------------------------------------
    # 14. Classify document
    # --------------------------------------------------------

    try:

        document_type = classify_document(
            extracted_text
        )

    except Exception as e:

        document.status = "failed"

        db.commit()

        raise HTTPException(
            status_code=500,
            detail=(
                "Document classification failed: "
                f"{str(e)}"
            ),
        )

    # --------------------------------------------------------
    # 15. Extract structured fields
    # --------------------------------------------------------

    try:

        extracted_fields = extract_financial_fields(
            extracted_text,
            document_type,
        )

    except Exception as e:

        # Mark document as failed
        document.status = "failed"

        db.commit()

        error_message = str(e)

        # ----------------------------------------------------
        # Handle Groq rate limit
        # ----------------------------------------------------

        if (
            "429" in error_message
            or "rate_limit_exceeded" in error_message
            or "Rate limit reached" in error_message
        ):

            raise HTTPException(
                status_code=429,
                detail=(
                    "LLM rate limit reached. "
                    "Please try again later."
                ),
            )

        # ----------------------------------------------------
        # Handle other field extraction errors
        # ----------------------------------------------------

        raise HTTPException(
            status_code=500,
            detail=(
                "Field extraction failed: "
                f"{error_message}"
            ),
        )

    # --------------------------------------------------------
    # 16. Add document type to extracted fields
    # --------------------------------------------------------

    if not isinstance(extracted_fields, dict):

        extracted_fields = {}

    extracted_fields["document_type"] = document_type

    # --------------------------------------------------------
    # 17. Save extracted data
    # --------------------------------------------------------

    document.extracted_text = extracted_text

    # IMPORTANT:
    # Document model uses SQLAlchemy JSON column.
    # Therefore save the Python dictionary directly.

    document.extracted_fields = extracted_fields

    document.status = "processed"

    db.commit()
    db.refresh(document)

    # --------------------------------------------------------
    # 18. Return response
    # --------------------------------------------------------

    return {
        "document_id": document.document_id,
        "filename": document.filename,
        "status": document.status,
        "document_type": document_type,
        "size_bytes": len(contents),
        "text_length": len(extracted_text),
        "extracted_fields": extracted_fields,
    }


# ============================================================
# GET DOCUMENT
# ============================================================

@router.get("/{document_id}")
def get_document(
    document_id: str,
    db: Session = Depends(get_db),
):

    # --------------------------------------------------------
    # 1. Find document
    # --------------------------------------------------------

    document = (
        db.query(Document)
        .filter(
            Document.document_id == document_id
        )
        .first()
    )

    # --------------------------------------------------------
    # 2. Check document exists
    # --------------------------------------------------------

    if not document:

        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    # --------------------------------------------------------
    # 3. Get extracted fields
    # --------------------------------------------------------

    extracted_fields = normalize_extracted_fields(
        document.extracted_fields
    )

    # --------------------------------------------------------
    # 4. Get document type from extracted fields
    # --------------------------------------------------------

    document_type = extracted_fields.get(
        "document_type"
    )

    # --------------------------------------------------------
    # 5. Return document
    # --------------------------------------------------------

    return {
        "document_id": document.document_id,
        "filename": document.filename,
        "status": document.status,
        "document_type": document_type,
        "file_path": document.file_path,
        "created_at": document.created_at,

        "text_length": (
            len(document.extracted_text)
            if document.extracted_text
            else 0
        ),

        "extracted_text": document.extracted_text,

        "extracted_fields": extracted_fields,
    }


# ============================================================
# GET ALL DOCUMENTS
# ============================================================

@router.get("/")
def get_all_documents(
    db: Session = Depends(get_db),
):
    """
    Return all uploaded documents.
    """

    # --------------------------------------------------------
    # 1. Get all documents
    # --------------------------------------------------------

    documents = (
        db.query(Document)
        .order_by(Document.created_at.desc())
        .all()
    )

    # --------------------------------------------------------
    # 2. Build response
    # --------------------------------------------------------

    result = []

    for document in documents:

        # Get JSON fields safely
        extracted_fields = normalize_extracted_fields(
            document.extracted_fields
        )

        # Get document type from extracted fields
        document_type = extracted_fields.get(
            "document_type"
        )

        result.append(
            {
                "document_id": document.document_id,
                "filename": document.filename,
                "status": document.status,
                "document_type": document_type,
                "file_path": document.file_path,
                "created_at": document.created_at,

                "text_length": (
                    len(document.extracted_text)
                    if document.extracted_text
                    else 0
                ),

                "extracted_fields": extracted_fields,
            }
        )

    # --------------------------------------------------------
    # 3. Return all documents
    # --------------------------------------------------------

    return {
        "total": len(result),
        "documents": result,
    }