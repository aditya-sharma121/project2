import json
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.incident import Incident
from app.models.evidence import Evidence
from app.models.verification import Verification
from app.models.user import User
from app.schemas.incident import IncidentRead, IncidentListResponse, IncidentStatusUpdate
from app.schemas.verification import VerificationRead
from app.core.security import get_current_user_optional, require_role
from app.services.gemini_service import gemini_service
from app.services.cloudinary_service import cloudinary_service
from app.services.verification_service import verification_service
from app.services.risk_service import risk_service
from app.websocket.manager import ws_manager

router = APIRouter(prefix="/incidents", tags=["Incidents"])


@router.post("", response_model=IncidentRead, status_code=status.HTTP_201_CREATED)
async def create_incident(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    latitude: float = Form(...),
    longitude: float = Form(...),
    reported_severity: str = Form("medium"),
    incident_type: str = Form("urban_flooding"),
    is_simulated: bool = Form(False),
    image: Optional[UploadFile] = File(None),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    user_id = current_user.id if current_user else None

    # Create incident record first
    incident = Incident(
        title=title,
        description=description,
        latitude=latitude,
        longitude=longitude,
        reported_severity=reported_severity.lower(),
        incident_type=incident_type,
        is_simulated=is_simulated,
        created_by=user_id,
        status="reported"
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)

    # Process image if provided
    if image:
        try:
            image_bytes = await image.read()
            # 1. Preprocess: validate, resize, sha256, phash
            preprocessed = gemini_service.preprocess_image(image_bytes)

            # 2. Duplicate check
            is_dup, dup_reason = verification_service.check_duplicate_image(
                preprocessed["sha256"], preprocessed["phash"], db
            )

            # 3. AI Assessment via Gemini Vision
            ai_assessment = None
            try:
                ai_assessment = await gemini_service.analyze_image(
                    preprocessed["optimized_bytes"], filename=image.filename or "flood.jpg"
                )
                incident.ai_severity = ai_assessment.severity
            except Exception as ai_err:
                # If Gemini is down or fails: manual report stays saved!
                incident.ai_severity = None

            # 4. Storage upload
            upload_meta = await cloudinary_service.upload_image(
                preprocessed["optimized_bytes"], filename=f"inc_{incident.id}_{image.filename}"
            )

            # 5. Save Evidence record
            evidence = Evidence(
                incident_id=incident.id,
                user_id=user_id,
                image_url=upload_meta["secure_url"],
                image_hash=preprocessed["sha256"],
                phash=preprocessed["phash"],
                visible_water=ai_assessment.visible_water if ai_assessment else False,
                ai_confidence=ai_assessment.confidence if ai_assessment else 0.0,
                ai_result=ai_assessment.model_dump() if ai_assessment else None,
                is_duplicate=is_dup
            )
            db.add(evidence)
            db.commit()

        except ValueError as val_err:
            # Client upload validation error (format, size)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(val_err)
            )
        except Exception as e:
            # Continue with incident saved even if image pipeline has non-fatal error
            pass

    # Calculate TrustScore and Priority Risk
    try:
        verification_service.calculate_trust_score(incident.id, db, verified_by="system")
        risk_service.compute_incident_risk(incident, db)
        risk_service.update_road_segment_risks(db)
    except Exception:
        pass

    db.refresh(incident)

    # Broadcast websocket event
    await ws_manager.broadcast("incident.created", {
        "id": incident.id,
        "title": incident.title,
        "latitude": incident.latitude,
        "longitude": incident.longitude,
        "reported_severity": incident.reported_severity,
        "ai_severity": incident.ai_severity,
        "confidence_score": incident.confidence_score,
        "risk_score": incident.risk_score,
        "is_simulated": incident.is_simulated
    })

    return incident


@router.get("", response_model=IncidentListResponse)
async def list_incidents(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    min_confidence: Optional[float] = None,
    hide_simulated: bool = False,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    query = db.query(Incident)
    if status:
        query = query.filter(Incident.status == status)
    if severity:
        query = query.filter(Incident.reported_severity == severity)
    if min_confidence is not None:
        query = query.filter(Incident.confidence_score >= min_confidence)
    if hide_simulated:
        query = query.filter(Incident.is_simulated.is_(False))

    total = query.count()
    items = query.order_by(Incident.risk_score.desc(), Incident.created_at.desc()).offset((page - 1) * limit).limit(limit).all()

    now = datetime.utcnow()
    for item in items:
        age_min = round((now - item.created_at).total_seconds() / 60.0, 1)
        item.freshness_minutes = age_min
        item.is_stale = age_min > 360.0

    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit
    }


@router.get("/{incident_id}", response_model=IncidentRead)
async def get_incident(incident_id: str, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident with id {incident_id} not found"
        )
    
    # Load evidence and latest verification
    evidence_items = db.query(Evidence).filter(Evidence.incident_id == incident_id).all()
    latest_verification = db.query(Verification).filter(
        Verification.incident_id == incident_id
    ).order_by(Verification.created_at.desc()).first()

    now = datetime.utcnow()
    age_min = round((now - incident.created_at).total_seconds() / 60.0, 1)

    incident.evidence = evidence_items
    incident.latest_verification = latest_verification
    incident.freshness_minutes = age_min
    incident.is_stale = age_min > 360.0

    return incident


@router.patch("/{incident_id}/status", response_model=IncidentRead)
async def update_incident_status(
    incident_id: str,
    update_data: IncidentStatusUpdate,
    current_user: User = Depends(require_role("operator")),
    db: Session = Depends(get_db)
):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")

    valid_statuses = ["reported", "under_review", "verified", "resolved", "rejected"]
    if update_data.status not in valid_statuses:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid status. Must be one of {valid_statuses}")

    old_status = incident.status
    incident.status = update_data.status
    incident.updated_at = datetime.utcnow()
    db.commit()

    # Recalculate road segment risks
    risk_service.update_road_segment_risks(db)

    # Broadcast status change event
    await ws_manager.broadcast("incident.status_changed", {
        "id": incident.id,
        "old_status": old_status,
        "new_status": incident.status,
        "updated_by": current_user.email,
        "note": update_data.note
    })

    return incident


@router.post("/{incident_id}/verify", response_model=VerificationRead)
async def re_verify_incident(
    incident_id: str,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    try:
        verifier = current_user.id if current_user else "system"
        verif = verification_service.calculate_trust_score(incident_id, db, verified_by=verifier)
        risk_service.compute_incident_risk(db.query(Incident).filter(Incident.id == incident_id).first(), db)
        risk_service.update_road_segment_risks(db)
        return verif
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{incident_id}/trust-score", response_model=VerificationRead)
async def get_incident_trust_score(incident_id: str, db: Session = Depends(get_db)):
    verif = db.query(Verification).filter(
        Verification.incident_id == incident_id
    ).order_by(Verification.created_at.desc()).first()
    if not verif:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No verification score generated yet")
    return verif
