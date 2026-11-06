from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.evidence import Evidence
from app.schemas.evidence import EvidenceRead

router = APIRouter(prefix="/evidence", tags=["Evidence"])


@router.get("", response_model=List[EvidenceRead])
async def list_evidence(incident_id: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Evidence)
    if incident_id:
        query = query.filter(Evidence.incident_id == incident_id)
    return query.order_by(Evidence.uploaded_at.desc()).all()


@router.get("/{evidence_id}", response_model=EvidenceRead)
async def get_evidence(evidence_id: str, db: Session = Depends(get_db)):
    ev = db.query(Evidence).filter(Evidence.id == evidence_id).first()
    if not ev:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evidence record not found")
    return ev
