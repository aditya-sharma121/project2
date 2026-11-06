from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class FacilityRead(BaseModel):
    id: str
    name: str
    facility_type: str
    capacity: int
    status: str
    latitude: float
    longitude: float
    distance_m: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True
