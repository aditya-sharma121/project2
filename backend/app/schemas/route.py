from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class LatLng(BaseModel):
    lat: float = Field(..., ge=-90.0, le=90.0)
    lng: float = Field(..., ge=-180.0, le=180.0)


class RouteCalculateRequest(BaseModel):
    origin: LatLng
    destination: LatLng
    avoid_high_risk: bool = True
    lambda_risk: Optional[float] = 5.0


class RoutePath(BaseModel):
    nodes: List[str]
    coordinates: List[List[float]]  # [ [lng, lat], ... ]
    distance_m: float
    total_risk: float
    estimated_duration_sec: float
    geometry: Dict[str, Any]  # GeoJSON LineString


class AvoidedEdge(BaseModel):
    edge: List[str]
    segment_id: Optional[str] = None
    name: Optional[str] = None
    risk_score: float
    reason: str


class RouteCalculateResponse(BaseModel):
    standard_route: Optional[RoutePath] = None
    risk_aware_route: Optional[RoutePath] = None
    avoided_segments: List[AvoidedEdge] = []
    distance_difference_m: float = 0.0
    risk_reduction_pct: float = 0.0
    computed_at: str
    disclaimer: str = "AFTERFLOW is an advisory decision-support prototype. Routes are not guaranteed safe. Always follow official directives."
