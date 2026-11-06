import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Boolean, DateTime, Index
from app.database.connection import Base, SafeLineString


class RoadSegment(Base):
    __tablename__ = "road_segments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    external_id = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=True)
    road_class = Column(String(50), default="primary", nullable=False)  # motorway, primary, secondary, residential

    start_node = Column(String(50), nullable=False, index=True)
    end_node = Column(String(50), nullable=False, index=True)
    distance_m = Column(Float, nullable=False, default=100.0)

    # Dynamic risk metrics
    risk_score = Column(Float, default=0.0, nullable=False)  # 0 to 100
    risk_level = Column(String(50), default="low", nullable=False)  # low, medium, high, critical
    is_blocked = Column(Boolean, default=False, nullable=False)

    geometry = Column(SafeLineString, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


Index("idx_road_risk_blocked", RoadSegment.risk_score, RoadSegment.is_blocked)
