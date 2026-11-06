from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from app.schemas.evidence import EvidenceRead
from app.schemas.verification import VerificationRead


class IncidentCreate(BaseModel):
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    incident_type: str = "urban_flooding"
    reported_severity: str = Field("medium", description="low, medium, high, critical")
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    is_simulated: bool = False


class IncidentStatusUpdate(BaseModel):
    status: str = Field(..., description="reported, under_review, verified, resolved, rejected")
    note: Optional[str] = None


class IncidentRead(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    incident_type: str
    reported_severity: str
    ai_severity: Optional[str] = None
    status: str
    confidence_score: float
    risk_score: float
    is_simulated: bool
    latitude: float
    longitude: float
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    freshness_minutes: Optional[float] = None
    is_stale: bool = False
    evidence: Optional[List[EvidenceRead]] = None
    latest_verification: Optional[VerificationRead] = None

    class Config:
        from_attributes = True


class IncidentListResponse(BaseModel):
    items: List[IncidentRead]
    total: int
    page: int
    limit: int
