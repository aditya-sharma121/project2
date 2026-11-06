from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class TrustScoreExplanation(BaseModel):
    geographic_agreement_reason: str
    temporal_agreement_reason: str
    visual_quality_reason: str
    independent_sources_reason: str
    summary: str


class VerificationRead(BaseModel):
    id: str
    incident_id: str
    verified_by: Optional[str] = None
    geographic_agreement: float
    temporal_agreement: float
    visual_quality: float
    independent_source_quality: float
    trust_score: float
    confidence_label: str
    explanation: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True
