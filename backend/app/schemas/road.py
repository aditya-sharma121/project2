from typing import Optional, List, Any, Dict
from datetime import datetime
from pydantic import BaseModel


class RoadSegmentRead(BaseModel):
    id: str
    external_id: str
    name: Optional[str] = None
    road_class: str
    start_node: str
    end_node: str
    distance_m: float
    risk_score: float
    risk_level: str
    is_blocked: bool
    updated_at: datetime

    class Config:
        from_attributes = True


class RoadBlockageUpdate(BaseModel):
    is_blocked: bool
    reason: Optional[str] = None
