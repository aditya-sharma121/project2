from fastapi import APIRouter

router = APIRouter(prefix="/evidence", tags=["Evidence"])


@router.get("")
async def list_evidence():
    return {"items": []}
