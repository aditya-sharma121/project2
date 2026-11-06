from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from app.schemas.incident import IncidentRead
from app.schemas.road import RoadSegmentRead


class DashboardKpis(BaseModel):
    active_incidents: int
    high_risk_incidents: int
    verified_incidents: int
    pending_review: int
    blocked_roads: int
    simulated_incidents: int


class TimelineEvent(BaseModel):
    id: str
    event_type: str
    incident_id: Optional[str] = None
    title: str
    description: str
    created_at: str
    metadata: Optional[Dict[str, Any]] = None
