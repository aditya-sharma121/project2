import base64
import logging
from typing import Dict, Any, Optional
from app.config import settings

logger = logging.getLogger("afterflow.cloudinary")


class CloudinaryStorageService:
    def __init__(self):
        self.cloud_name = settings.CLOUDINARY_CLOUD_NAME
        self.api_key = settings.CLOUDINARY_API_KEY
        self.api_secret = settings.CLOUDINARY_API_SECRET
        self._configured = False

        if self.cloud_name and self.api_key and self.api_secret:
            try:
                import cloudinary
                import cloudinary.uploader
                cloudinary.config(
                    cloud_name=self.cloud_name,
                    api_key=self.api_key,
                    api_secret=self.api_secret,
                    secure=True
                )
                self._configured = True
            except Exception as e:
                logger.warning(f"Failed to initialize Cloudinary SDK: {e}")

    async def upload_image(self, file_bytes: bytes, filename: str) -> Dict[str, Any]:
        """Upload image to Cloudinary or create a self-contained data URL fallback."""
        if self._configured:
            try:
                import cloudinary.uploader
                upload_result = cloudinary.uploader.upload(
                    file_bytes,
                    folder="afterflow/evidence",
                    resource_type="image",
                    transformation=[
                        {"quality": "auto", "fetch_format": "auto"}
                    ]
                )
                return {
                    "secure_url": upload_result.get("secure_url"),
                    "public_id": upload_result.get("public_id"),
                    "format": upload_result.get("format")
                }
            except Exception as e:
                logger.error(f"Cloudinary upload failed: {e}. Falling back to internal data uri.")

        # Self-contained fallback URL
        b64_data = base64.b64encode(file_bytes).decode("utf-8")
        data_uri = f"data:image/jpeg;base64,{b64_data}"
        return {
            "secure_url": data_uri,
            "public_id": f"local_{filename}",
            "format": "jpeg"
        }


cloudinary_service = CloudinaryStorageService()
