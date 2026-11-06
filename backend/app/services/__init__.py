from app.services.gemini_service import GeminiVisionService, gemini_service
from app.services.cloudinary_service import CloudinaryStorageService, cloudinary_service
from app.services.verification_service import VerificationService, verification_service
from app.services.risk_service import RiskService, risk_service
from app.services.geospatial_service import GeospatialService, geospatial_service
from app.services.routing_service import RoutingEngine, routing_engine, DEFAULT_EDGES

# Backwards compatible alias
GeminiService = GeminiVisionService
CloudinaryService = CloudinaryStorageService

__all__ = [
    "GeminiVisionService",
    "GeminiService",
    "gemini_service",
    "CloudinaryStorageService",
    "CloudinaryService",
    "cloudinary_service",
    "VerificationService",
    "verification_service",
    "RiskService",
    "risk_service",
    "GeospatialService",
    "geospatial_service",
    "RoutingEngine",
    "routing_engine",
    "DEFAULT_EDGES",
]
