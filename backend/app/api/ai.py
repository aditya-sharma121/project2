from fastapi import APIRouter

router = APIRouter(prefix="/ai", tags=["AI Assessment"])


@router.get("/status")
async def ai_status():
    return {"status": "ready", "provider": "google-genai", "depth_inference": "disabled"}
