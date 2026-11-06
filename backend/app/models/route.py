import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, Index
from sqlalchemy.types import JSON
from app.database.connection import Base, SafeLineString


class RouteLog(Base):
    __tablename__ = "routes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String(36), nullable=True)

    origin_lat = Column(Float, nullable=False)
    origin_lng = Column(Float, nullable=False)
    dest_lat = Column(Float, nullable=False)
    dest_lng = Column(Float, nullable=False)

    distance_m = Column(Float, nullable=False)
    total_risk = Column(Float, nullable=False, default=0.0)
    avoided_segments = Column(JSON, nullable=True)

    geometry = Column(SafeLineString, nullable=True)
    computed_at = Column(DateTime, default=datetime.utcnow, nullable=False)


Index("idx_routes_computed", RouteLog.computed_at)
