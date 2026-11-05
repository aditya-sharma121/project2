"""Cloudinary image upload service skeleton."""
from typing import Dict, Any


class CloudinaryService:
    def __init__(self, cloud_name: str = "", api_key: str = "", api_secret: str = ""):
        self.cloud_name = cloud_name
        self.api_key = api_key
        self.api_secret = api_secret

    async def upload_image(self, file_bytes: bytes, filename: str) -> Dict[str, Any]:
        """Upload optimized image and return secure URL and public id."""
        return {
            "secure_url": f"https://res.cloudinary.com/demo/image/upload/{filename}",
            "public_id": f"afterflow/{filename}"
        }
