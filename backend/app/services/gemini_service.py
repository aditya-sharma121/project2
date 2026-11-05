"""Google Gemini Vision assessment service skeleton."""
from typing import Dict, Any, Optional


class GeminiService:
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.5-flash", mock: bool = True):
        self.api_key = api_key
        self.model = model
        self.mock = mock

    async def analyze_flood_image(self, image_bytes: bytes) -> Dict[str, Any]:
        """Analyze image for flood evidence without inferring water depth."""
        return {
            "classification": "likely_flooding",
            "visible_water": True,
            "severity": "medium",
            "estimated_coverage": 0.65,
            "confidence": 0.88,
            "limitations": [
                "Water depth cannot be inferred from 2D photographic perspective",
                "Subsurface terrain and submerged hazards are not visible"
            ]
        }
