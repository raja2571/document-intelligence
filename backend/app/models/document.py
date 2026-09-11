from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text, JSON

from backend.app.core.database import Base


class Document(Base):
    __tablename__ = "documents"

    # ============================================================
    # PRIMARY KEY
    # ============================================================

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    # ============================================================
    # DOCUMENT ID
    # ============================================================

    document_id = Column(
        String,
        unique=True,
        nullable=False,
        index=True,
    )

    # ============================================================
    # FILE INFORMATION
    # ============================================================

    filename = Column(
        String,
        nullable=False,
    )

    file_path = Column(
        String,
        nullable=False,
    )

    # ============================================================
    # PROCESSING STATUS
    # ============================================================

    status = Column(
        String,
        nullable=False,
        default="uploaded",
    )

    # ============================================================
    # DOCUMENT TYPE
    # ============================================================

    document_type = Column(
        String,
        nullable=True,
    )

    # ============================================================
    # EXTRACTED TEXT
    # ============================================================

    extracted_text = Column(
        Text,
        nullable=True,
    )

    # ============================================================
    # EXTRACTED STRUCTURED FIELDS
    # ============================================================

    extracted_fields = Column(
        JSON,
        nullable=True,
    )

    # ============================================================
    # CREATED DATE
    # ============================================================

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )