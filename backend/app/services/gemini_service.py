import io
import json
import logging
from typing import Dict, Any, List, Optional
from PIL import Image, ImageOps
import hashlib
import imagehash
from pydantic import ValidationError

from app.config import settings
from app.schemas.evidence import FloodAssessment

logger = logging.getLogger("afterflow.gemini")

FLOOD_PROMPT = """
You are AFTERFLOW's vision intelligence module.
Assess VISIBLE flood evidence only from this urban street/road photo.
Return a valid JSON object matching this schema:
{
  "classification": "no_flooding" | "possible_flooding" | "likely_flooding" | "unclear",
  "visible_water": boolean,
  "severity": "none" | "low" | "medium" | "high",
  "estimated_coverage": float between 0.0 and 1.0 (portion of road surface covered),
  "confidence": float between 0.0 and 1.0,
  "limitations": [string list of technical limitations]
}

CRITICAL RULES:
1. Do NOT infer actual water depth from the photo under any circumstances.
2. Only assess visible surface water, waterlogged road areas, submerged vehicle tires, or surface reflection.
3. Always include explicit limitations (e.g. water depth cannot be measured from 2D angle, hidden submerged potholes/debris).
4. Output raw JSON only.
"""


class GeminiVisionService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = settings.GEMINI_MODEL
        self.mock_ai = settings.MOCK_AI
        self._client = None

        if self.api_key and not self.mock_ai:
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Could not initialize google-genai client: {e}. Falling back to mock mode.")

    def preprocess_image(self, image_bytes: bytes) -> Dict[str, Any]:
        """Validates format, size, orientation, computes SHA-256 and pHash, and resizes."""
        # Validate size: max 5MB
        if len(image_bytes) > 5 * 1024 * 1024:
            raise ValueError("Image file exceeds maximum allowable size of 5MB")

        # Open and validate image
        try:
            image = Image.open(io.BytesIO(image_bytes))
            image.verify()
            image = Image.open(io.BytesIO(image_bytes))
        except Exception:
            raise ValueError("Invalid or corrupted image format. Allowed types: JPEG, PNG, WEBP.")

        if image.format.lower() not in ["jpeg", "jpg", "png", "webp"]:
            raise ValueError(f"Unsupported image format: {image.format}. Allowed types: JPEG, PNG, WEBP.")

        # Transpose EXIF orientation
        try:
            image = ImageOps.exif_transpose(image)
        except Exception:
            pass

        # Compute SHA-256
        sha256_hash = hashlib.sha256(image_bytes).hexdigest()

        # Compute perceptual hash (pHash)
        phash_val = str(imagehash.phash(image))

        # Resize to max 1280px along longest edge
        max_dim = 1280
        w, h = image.size
        if max(w, h) > max_dim:
            if w > h:
                new_w = max_dim
                new_h = int(h * (max_dim / w))
            else:
                new_h = max_dim
                new_w = int(w * (max_dim / h))
            image = image.resize((new_w, new_h), Image.Resampling.LANCZOS)

        # Re-encode optimized JPEG
        buffer = io.BytesIO()
        if image.mode != "RGB":
            image = image.convert("RGB")
        image.save(buffer, format="JPEG", quality=85, optimize=True)
        optimized_bytes = buffer.getvalue()

        return {
            "sha256": sha256_hash,
            "phash": phash_val,
            "width": image.width,
            "height": image.height,
            "optimized_bytes": optimized_bytes
        }

    async def analyze_image(self, image_bytes: bytes, filename: str = "image.jpg") -> FloodAssessment:
        """Runs Gemini Vision model on image bytes or returns deterministic mock assessment."""
        if self.mock_ai or not self._client:
            # Deterministic mock based on hash or filename
            is_clear = "clear" in filename.lower()
            if is_clear:
                return FloodAssessment(
                    classification="no_flooding",
                    visible_water=False,
                    severity="none",
                    estimated_coverage=0.0,
                    confidence=0.92,
                    limitations=[
                        "Water depth cannot be inferred from 2D photographic perspective",
                        "Assessment reflects only visible surface area in camera frame"
                    ]
                )
            return FloodAssessment(
                classification="likely_flooding",
                visible_water=True,
                severity="medium",
                estimated_coverage=0.65,
                confidence=0.88,
                limitations=[
                    "Water depth cannot be inferred from 2D photographic perspective",
                    "Submerged potholes, curb drop-offs, and open manholes are not visible",
                    "Camera perspective may distort surface water extent"
                ]
            )

        # Call real Gemini API
        for attempt in range(2):  # retry once on JSON error
            try:
                from google.genai import types
                response = self._client.models.generate_content(
                    model=self.model_name,
                    contents=[
                        types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                        FLOOD_PROMPT
                    ],
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.1
                    )
                )

                text_resp = response.text
                parsed_json = json.loads(text_resp)
                assessment = FloodAssessment(**parsed_json)
                return assessment
            except (json.JSONDecodeError, ValidationError) as e:
                logger.warning(f"Gemini output parsing failed (attempt {attempt + 1}/2): {e}")
                if attempt == 1:
                    raise RuntimeError("Gemini AI generated invalid response format after retry.")
            except Exception as e:
                logger.error(f"Gemini API invocation error: {e}")
                raise RuntimeError(f"Gemini Vision service unavailable: {str(e)}")


gemini_service = GeminiVisionService()
