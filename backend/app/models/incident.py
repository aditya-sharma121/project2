import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Boolean, DateTime, Text, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import JSON
from app.database.connection import Base, SafePoint


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    incident_type = Column(String(100), default="urban_flooding", nullable=False)
    
    # Severity & Scores
    reported_severity = Column(String(50), nullable=False, default="medium")  # low, medium, high, critical
    ai_severity = Column(String(50), nullable=True)  # none, low, medium, high
    status = Column(String(50), nullable=False, default="reported", index=True)  # reported, under_review, verified, resolved, rejected
    confidence_score = Column(Float, default=0.0, nullable=False)  # TrustScore 0-100
    risk_score = Column(Float, default=0.0, nullable=False)  # Priority risk score 0-100
    is_simulated = Column(Boolean, default=False, nullable=False)

    # Location
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    location = Column(SafePoint, nullable=True)

    created_by = Column(String(36), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


# Spatial and attribute index
Index("idx_incidents_status_created", Incident.status, Incident.created_at)
Index("idx_incidents_coords", Incident.latitude, Incident.longitude)
