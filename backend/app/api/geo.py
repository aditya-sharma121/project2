from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.incident import Incident
from app.models.road_segment import RoadSegment
from app.services.geospatial_service import geospatial_service
from app.services.routing_service import DEFAULT_EDGES

router = APIRouter(prefix="/geo", tags=["Geospatial"])


@router.get("/incidents")
async def get_incident_geojson(
    status: Optional[str] = None,
    hide_simulated: bool = False,
    db: Session = Depends(get_db)
):
    """Returns flood incidents as a GeoJSON FeatureCollection."""
    query = db.query(Incident)
    if status:
        query = query.filter(Incident.status == status)
    if hide_simulated:
        query = query.filter(Incident.is_simulated.is_(False))

    incidents = query.all()
    return geospatial_service.incidents_to_geojson(incidents)


@router.get("/road-risks")
async def get_road_risks_geojson(db: Session = Depends(get_db)):
    """Returns road network segments and risk levels as a GeoJSON FeatureCollection."""
    roads = db.query(RoadSegment).all()

    # Seed in-memory defaults if table is empty
    if not roads:
        for edge in DEFAULT_EDGES:
            seg = RoadSegment(
                external_id=edge["id"],
                name=edge["name"],
                start_node=edge["u"],
                end_node=edge["v"],
                distance_m=edge["distance_m"],
                risk_score=edge["risk_score"],
                risk_level="low",
                is_blocked=edge["is_blocked"]
            )
            db.add(seg)
        db.commit()
        roads = db.query(RoadSegment).all()

    return geospatial_service.road_risks_to_geojson(roads)
