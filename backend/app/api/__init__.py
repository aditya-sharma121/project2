from fastapi import APIRouter
from app.api.auth import router as auth_router
from app.api.incidents import router as incidents_router
from app.api.evidence import router as evidence_router
from app.api.ai import router as ai_router
from app.api.geo import router as geo_router
from app.api.routes import router as routes_router
from app.api.dashboard import router as dashboard_router
from app.api.weather import router as weather_router
from app.api.facilities import router as facilities_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router)
api_router.include_router(incidents_router)
api_router.include_router(evidence_router)
api_router.include_router(ai_router)
api_router.include_router(geo_router)
api_router.include_router(routes_router)
api_router.include_router(dashboard_router)
api_router.include_router(weather_router)
api_router.include_router(facilities_router)
