from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[Any] = None


class ErrorResponse(BaseModel):
    error: ErrorDetail


class StandardResponse(BaseModel):
    success: bool = True
    data: Optional[Any] = None
    message: Optional[str] = None
