import json
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "AFTERFLOW"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    
    # CORS
    CORS_ORIGINS: Union[List[str], str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                return [v]
        return v

    # Security & Auth
    JWT_SECRET: str = "afterflow-secret-key-change-in-production-1234567890"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    # Database
    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@localhost:5432/afterflow"

    # AI (Gemini)
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"
    MOCK_AI: bool = True

    # Storage (Cloudinary)
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""

    # Operational defaults
    ROUTING_LAMBDA: float = 5.0
    VERIFICATION_RADIUS_METERS: float = 200.0
    VERIFICATION_WINDOW_HOURS: float = 6.0
    DEFAULT_LAT: float = 27.1767
    DEFAULT_LNG: float = 78.0081

    # App disclaimer notice
    DISCLAIMER: str = (
        "AFTERFLOW is a prototype decision-support tool, not an official emergency dispatch service. "
        "Routes and flood assessments are advisory and not guaranteed safe. Always follow official civil defense guidance."
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
