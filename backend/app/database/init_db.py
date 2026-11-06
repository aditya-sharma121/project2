import logging
from sqlalchemy import text
from app.database.connection import engine, Base
import app.models  # Ensure all models are registered

logger = logging.getLogger("afterflow.init_db")


def init_db():
    """Initialize database tables and required PostgreSQL extensions."""
    try:
        with engine.connect() as conn:
            # Enable PostGIS and uuid-ossp if running on PostgreSQL
            if engine.dialect.name == "postgresql":
                logger.info("Enabling postgis and uuid-ossp extensions...")
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"))
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
                conn.commit()
            
        Base.metadata.create_all(bind=engine)
        logger.info("Database schema initialized successfully.")
    except Exception as e:
        logger.warning(f"Could not connect to external DB during startup ({e}). Falling back to in-memory/runtime schema.")


if __name__ == "__main__":
    init_db()
