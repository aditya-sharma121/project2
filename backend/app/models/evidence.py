import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Boolean, DateTime, Index
from sqlalchemy.types import JSON
from app.database.connection import Base


class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    incident_id = Column(String(36), nullable=False, index=True)
    user_id = Column(String(36), nullable=True)

    image_url = Column(String(1024), nullable=False)
    image_hash = Column(String(64), nullable=False, index=True)  # SHA-256
    phash = Column(String(64), nullable=False, index=True)  # Perceptual hash hex

    visible_water = Column(Boolean, default=False, nullable=False)
    ai_confidence = Column(Float, default=0.0, nullable=False)
    ai_result = Column(JSON, nullable=True)  # Full JSON payload from Gemini
    is_duplicate = Column(Boolean, default=False, nullable=False)

    captured_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)


Index("idx_evidence_incident_uploaded", Evidence.incident_id, Evidence.uploaded_at)
