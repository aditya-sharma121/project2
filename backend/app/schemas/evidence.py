from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field


class FloodAssessment(BaseModel):
    """Strict Gemini image assessment output schema.
    Rule: AI must NEVER infer exact water depth from photo.
    """
    classification: str = Field(..., description="no_flooding | possible_flooding | likely_flooding | unclear")
    visible_water: bool = Field(..., description="Whether standing or running water is visible")
    severity: str = Field(..., description="none | low | medium | high")
    estimated_coverage: float = Field(..., ge=0.0, le=1.0, description="Estimated flooded road surface coverage")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in visible water assessment")
    limitations: List[str] = Field(
        default_factory=lambda: [
            "Water depth cannot be inferred from 2D photographic perspective",
            "Submerged obstacles, potholes, and currents are not visible"
        ],
        description="Explicit technical limitations"
    )


class EvidenceRead(BaseModel):
    id: str
    incident_id: str
    user_id: Optional[str] = None
    image_url: str
    image_hash: str
    phash: str
    visible_water: bool
    ai_confidence: float
    ai_result: Optional[Dict[str, Any]] = None
    is_duplicate: bool
    captured_at: datetime
    uploaded_at: datetime

    class Config:
        from_attributes = True
