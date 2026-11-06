import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum
from app.database.connection import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(String(50), nullable=False, default="citizen")  # citizen, operator
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
