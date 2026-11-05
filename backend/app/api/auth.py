from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.get("/me")
async def get_me():
    return {"id": "00000000-0000-0000-0000-000000000000", "role": "citizen", "email": "anonymous@afterflow.local"}
