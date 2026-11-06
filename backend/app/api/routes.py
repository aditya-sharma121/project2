from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.road_segment import RoadSegment
from app.models.user import User
from app.schemas.route import RouteCalculateRequest, RouteCalculateResponse, LatLng
from app.schemas.road import RoadBlockageUpdate, RoadSegmentRead
from app.services.routing_service import routing_engine
from app.core.security import require_role
from app.websocket.manager import ws_manager

router = APIRouter(prefix="/routes", tags=["Routes"])


@router.post("/calculate", response_model=RouteCalculateResponse)
async def calculate_route(req: RouteCalculateRequest):
    """Calculates both plain shortest path and hazard-aware Dijkstra route."""
    try:
        response = routing_engine.calculate_routes(
            origin=req.origin,
            destination=req.destination,
            avoid_high_risk=req.avoid_high_risk,
            lambda_val=req.lambda_risk
        )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Route calculation error: {str(e)}"
        )


@router.patch("/segments/{segment_id}/block", response_model=RoadSegmentRead)
async def toggle_road_blockage(
    segment_id: str,
    update: RoadBlockageUpdate,
    current_user: User = Depends(require_role("operator")),
    db: Session = Depends(get_db)
):
    """Operator action to manually block or unblock a road segment."""
    road = db.query(RoadSegment).filter(
        (RoadSegment.id == segment_id) | (RoadSegment.external_id == segment_id)
    ).first()
    
    if not road:
        # Create or update synthetic segment if not already in DB
        road = RoadSegment(
            external_id=segment_id,
            name=f"Segment {segment_id}",
            start_node="node_1",
            end_node="node_2",
            distance_m=500.0,
            risk_score=100.0 if update.is_blocked else 0.0,
            risk_level="critical" if update.is_blocked else "low",
            is_blocked=update.is_blocked
        )
        db.add(road)
    else:
        road.is_blocked = update.is_blocked
        road.risk_score = 100.0 if update.is_blocked else 20.0
        road.risk_level = "critical" if update.is_blocked else "low"

    db.commit()
    db.refresh(road)

    # Update in-memory graph
    routing_engine.update_edge_risk(road.external_id, road.risk_score, road.is_blocked)

    # Broadcast websocket event
    await ws_manager.broadcast("route.hazard_updated", {
        "segment_id": road.external_id,
        "is_blocked": road.is_blocked,
        "risk_score": road.risk_score,
        "reason": update.reason or "Operator manual override"
    })

    return road


@router.get("/status")
async def routing_status():
    return {
        "status": "ready",
        "engine": "networkx-dijkstra",
        "nodes_loaded": len(routing_engine.nodes),
        "edges_loaded": len(routing_engine.graph.edges),
        "disclaimer": "Routes are advisory decision-support calculations and not guaranteed safe."
    }
