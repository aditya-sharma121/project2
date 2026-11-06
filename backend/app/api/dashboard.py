from typing import List, Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.incident import Incident
from app.models.road_segment import RoadSegment
from app.models.verification import Verification
from app.models.evidence import Evidence
from app.schemas.dashboard import DashboardKpis, TimelineEvent

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/kpis", response_model=DashboardKpis)
async def get_dashboard_kpis(db: Session = Depends(get_db)):
    active = db.query(Incident).filter(Incident.status.in_(["reported", "under_review", "verified"])).count()
    high_risk = db.query(Incident).filter(Incident.risk_score >= 70.0).count()
    verified = db.query(Incident).filter(Incident.status == "verified").count()
    pending = db.query(Incident).filter(Incident.status.in_(["reported", "under_review"])).count()
    blocked = db.query(RoadSegment).filter(RoadSegment.is_blocked.is_(True)).count()
    simulated = db.query(Incident).filter(Incident.is_simulated.is_(True)).count()

    return DashboardKpis(
        active_incidents=active,
        high_risk_incidents=high_risk,
        verified_incidents=verified,
        pending_review=pending,
        blocked_roads=blocked,
        simulated_incidents=simulated
    )


@router.get("/timeline", response_model=List[TimelineEvent])
async def get_dashboard_timeline(db: Session = Depends(get_db)):
    events: List[TimelineEvent] = []

    # Recent incidents
    recent_incidents = db.query(Incident).order_by(Incident.created_at.desc()).limit(10).all()
    for inc in recent_incidents:
        events.append(TimelineEvent(
            id=f"inc_{inc.id}",
            event_type="incident.created",
            incident_id=inc.id,
            title=f"New report: {inc.title}",
            description=f"Reported severity: {inc.reported_severity.upper()} | TrustScore: {inc.confidence_score:.1f}",
            created_at=inc.created_at.isoformat()
        ))

    # Recent verifications
    recent_verifs = db.query(Verification).order_by(Verification.created_at.desc()).limit(10).all()
    for ver in recent_verifs:
        events.append(TimelineEvent(
            id=f"ver_{ver.id}",
            event_type="incident.verified",
            incident_id=ver.incident_id,
            title=f"TrustScore Updated ({ver.confidence_label})",
            description=f"Score: {ver.trust_score:.1f}/100 | Verified by: {ver.verified_by or 'system'}",
            created_at=ver.created_at.isoformat()
        ))

    events.sort(key=lambda x: x.created_at, reverse=True)
    return events[:15]


@router.get("/explainability/{incident_id}")
async def get_incident_explainability(incident_id: str, db: Session = Depends(get_db)):
    """Explainability panel: evidence factors + roads avoided because of this incident."""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")

    latest_verif = db.query(Verification).filter(
        Verification.incident_id == incident_id
    ).order_by(Verification.created_at.desc()).first()

    evidences = db.query(Evidence).filter(Evidence.incident_id == incident_id).all()

    # Determine affected roads
    roads = db.query(RoadSegment).filter(RoadSegment.risk_score >= 50.0).all()
    affected_roads = [
        {
            "segment_id": r.external_id,
            "name": r.name,
            "risk_score": r.risk_score,
            "risk_level": r.risk_level,
            "is_blocked": r.is_blocked
        }
        for r in roads
    ]

    return {
        "incident_id": incident.id,
        "title": incident.title,
        "status": incident.status,
        "priority_risk_score": incident.risk_score,
        "trust_score": incident.confidence_score,
        "is_simulated": incident.is_simulated,
        "confidence_label": latest_verif.confidence_label if latest_verif else "Unverified",
        "evidence_count": len(evidences),
        "factors": latest_verif.explanation if latest_verif else {},
        "affected_roads_avoided": affected_roads
    }
