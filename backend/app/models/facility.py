import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, Index
from app.database.connection import Base, SafePoint


class Facility(Base):
    __tablename__ = "facilities"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    name = Column(String(255), nullable=False)
    facility_type = Column(String(50), nullable=False)  # hospital, shelter, fire_station
    capacity = Column(Integer, default=100, nullable=False)
    status = Column(String(50), default="operational", nullable=False)  # operational, full, offline

    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    location = Column(SafePoint, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


Index("idx_facilities_type", Facility.facility_type)
Index("idx_facilities_coords", Facility.latitude, Facility.longitude)
