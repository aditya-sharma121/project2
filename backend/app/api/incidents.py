from fastapi import APIRouter

router = APIRouter(prefix="/incidents", tags=["Incidents"])


@router.get("")
async def list_incidents():
    return {"items": [], "total": 0}
