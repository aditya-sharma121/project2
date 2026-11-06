from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.facility import Facility
from app.schemas.facility import FacilityRead
from app.services.verification_service import haversine_distance_meters

router = APIRouter(prefix="/facilities", tags=["Facilities"])

# Default seeded facilities around Agra
SEED_FACILITIES = [
    {"name": "District Emergency Hospital", "facility_type": "hospital", "lat": 27.1850, "lng": 78.0100, "capacity": 250},
    {"name": "Municipal Central Flood Shelter", "facility_type": "shelter", "lat": 27.1740, "lng": 78.0140, "capacity": 500},
    {"name": "City Fire & Rescue Station #4", "facility_type": "fire_station", "lat": 27.1720, "lng": 78.0040, "capacity": 40},
    {"name": "St. John Community Relief Center", "facility_type": "shelter", "lat": 27.1810, "lng": 78.0130, "capacity": 300},
]


@router.get("/nearby", response_model=List[FacilityRead])
async def get_nearby_facilities(
    lat: float = Query(27.1767, ge=-90.0, le=90.0),
    lng: float = Query(78.0081, ge=-180.0, le=180.0),
    radius_m: float = Query(5000.0, ge=100.0, le=50000.0),
    facility_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Retrieves critical emergency facilities sorted by proximity."""
    facilities = db.query(Facility).all()

    # Seed if database table is currently empty
    if not facilities:
        for seed_data in SEED_FACILITIES:
            fac = Facility(
                name=seed_data["name"],
                facility_type=seed_data["facility_type"],
                latitude=seed_data["lat"],
                longitude=seed_data["lng"],
                capacity=seed_data["capacity"],
                status="operational"
            )
            db.add(fac)
        db.commit()
        facilities = db.query(Facility).all()

    results = []
    for fac in facilities:
        if facility_type and fac.facility_type != facility_type:
            continue
        dist = haversine_distance_meters(lat, lng, fac.latitude, fac.longitude)
        if dist <= radius_m:
            fac_read = FacilityRead(
                id=fac.id,
                name=fac.name,
                facility_type=fac.facility_type,
                capacity=fac.capacity,
                status=fac.status,
                latitude=fac.latitude,
                longitude=fac.longitude,
                distance_m=round(dist, 1),
                created_at=fac.created_at
            )
            results.append(fac_read)

    results.sort(key=lambda x: x.distance_m or 0.0)
    return results
