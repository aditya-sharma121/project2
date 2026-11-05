from fastapi import APIRouter

router = APIRouter(prefix="/geo", tags=["Geospatial"])


@router.get("/incidents")
async def get_incident_geojson():
    return {"type": "FeatureCollection", "features": []}


@router.get("/road-risks")
async def get_road_risks_geojson():
    return {"type": "FeatureCollection", "features": []}
