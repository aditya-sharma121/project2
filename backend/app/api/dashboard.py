from fastapi import APIRouter

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/kpis")
async def get_dashboard_kpis():
    return {
        "active_incidents": 0,
        "high_risk_incidents": 0,
        "verified_incidents": 0,
        "pending_review": 0
    }
