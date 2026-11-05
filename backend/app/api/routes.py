from fastapi import APIRouter

router = APIRouter(prefix="/routes", tags=["Routes"])


@router.get("/status")
async def routing_status():
    return {
        "status": "ready",
        "engine": "networkx-dijkstra",
        "disclaimer": "Routes are advisory decision-support calculations and not guaranteed safe."
    }
