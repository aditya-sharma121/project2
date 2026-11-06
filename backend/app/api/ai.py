from fastapi import APIRouter, UploadFile, File, HTTPException, status
from app.services.gemini_service import gemini_service
from app.schemas.evidence import FloodAssessment

router = APIRouter(prefix="/ai", tags=["AI Assessment"])


@router.post("/analyze-image", response_model=FloodAssessment)
async def analyze_flood_image(image: UploadFile = File(...)):
    """Analyze visible flood evidence via Gemini Vision AI.
    HARD RULE: AI must NEVER infer water depth from photo.
    """
    try:
        image_bytes = await image.read()
        preprocessed = gemini_service.preprocess_image(image_bytes)
        assessment = await gemini_service.analyze_image(
            preprocessed["optimized_bytes"], filename=image.filename or "flood.jpg"
        )
        return assessment
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI Vision assessment unavailable: {str(e)}"
        )


@router.get("/status")
async def ai_status():
    return {
        "status": "ready",
        "provider": "google-genai",
        "model": gemini_service.model_name,
        "mock_mode": gemini_service.mock_ai,
        "depth_inference": "disabled",
        "disclaimer": "Photographic assessment indicates visible surface water only. Depth cannot be inferred."
    }
