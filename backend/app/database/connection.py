import os
import logging
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.types import TypeDecorator, String, Text
from geoalchemy2 import Geography, Geometry
from app.config import settings

logger = logging.getLogger("afterflow.database")

DATABASE_URL = settings.DATABASE_URL
connect_args = {}

if os.environ.get("USE_SQLITE", "false").lower() == "true":
    DATABASE_URL = "sqlite:///afterflow_local.db"
    connect_args = {"check_same_thread": False}
    engine = create_engine(DATABASE_URL, connect_args=connect_args)
else:
    try:
        if DATABASE_URL.startswith("postgresql"):
            test_engine = create_engine(
                DATABASE_URL,
                pool_pre_ping=True,
                connect_args={"connect_timeout": 1}
            )
            with test_engine.connect() as conn:
                pass
            engine = test_engine
            logger.info("Connected to PostgreSQL PostGIS database.")
        else:
            engine = create_engine(DATABASE_URL, connect_args=connect_args)
    except Exception as e:
        logger.warning(f"PostgreSQL connection failed ({e}). Falling back to local SQLite engine (afterflow_local.db).")
        DATABASE_URL = "sqlite:///afterflow_local.db"
        connect_args = {"check_same_thread": False}
        engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class SafePoint(TypeDecorator):
    """PostGIS Geography Point in PostgreSQL; String in SQLite."""
    impl = String
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(Geography(geometry_type="POINT", srid=4326))
        return dialect.type_descriptor(String(255))


class SafeLineString(TypeDecorator):
    """PostGIS Geometry LineString in PostgreSQL; Text in SQLite."""
    impl = Text
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(Geometry(geometry_type="LINESTRING", srid=4326))
        return dialect.type_descriptor(Text)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
