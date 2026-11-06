import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, Index
from sqlalchemy.types import JSON
from app.database.connection import Base


class Verification(Base):
    __tablename__ = "verifications"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    incident_id = Column(String(36), nullable=False, index=True)
    verified_by = Column(String(36), nullable=True)  # System or operator user id

    # Component scores 0 - 100
    geographic_agreement = Column(Float, nullable=False, default=0.0)  # G
    temporal_agreement = Column(Float, nullable=False, default=0.0)    # Tm
    visual_quality = Column(Float, nullable=False, default=0.0)        # V
    independent_source_quality = Column(Float, nullable=False, default=0.0)  # I

    # TrustScore = 0.25G + 0.20Tm + 0.35V + 0.20I
    trust_score = Column(Float, nullable=False, default=0.0)
    confidence_label = Column(String(50), nullable=False, default="Unverified")  # Unverified, Probable, Strong evidence, High-confidence evidence
    explanation = Column(JSON, nullable=True)  # Detailed factors explanation

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


# Append-only audit history index
Index("idx_verifications_incident_created", Verification.incident_id, Verification.created_at)
