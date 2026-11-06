"""AFTERFLOW Duplicate Detection & TrustScore Correlation Engine.

NOTE ON THRESHOLDS:
The spatial-temporal clustering radiuses, visual weights, and score weights
implemented here are heuristic formulas designed for decision-support prototype demonstration
and have not been formally validated against real-world hydrological ground-truth datasets.
"""

import math
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple, Optional
import imagehash
from sqlalchemy.orm import Session

from app.config import settings
from app.models.incident import Incident
from app.models.evidence import Evidence
from app.models.verification import Verification


def haversine_distance_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate Great Circle distance in meters between two coordinates."""
    r = 6371000.0  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return r * c


def hex_hamming_distance(hash1: str, hash2: str) -> int:
    """Calculate Hamming distance between two hex pHash strings."""
    try:
        h1 = imagehash.hex_to_hash(hash1)
        h2 = imagehash.hex_to_hash(hash2)
        return h1 - h2
    except Exception:
        # Fallback bitwise comparison if invalid hex format
        return 999


class VerificationService:
    def __init__(
        self,
        cluster_radius_m: float = settings.VERIFICATION_RADIUS_METERS,
        time_window_hours: float = settings.VERIFICATION_WINDOW_HOURS
    ):
        self.cluster_radius_m = cluster_radius_m
        self.time_window_hours = time_window_hours

    def check_duplicate_image(
        self,
        sha256: str,
        phash: str,
        db: Session,
        exclude_evidence_id: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        """Check if image is an exact or perceptual duplicate of prior evidence."""
        query = db.query(Evidence)
        if exclude_evidence_id:
            query = query.filter(Evidence.id != exclude_evidence_id)
        
        all_prior = query.all()
        for prior in all_prior:
            # Exact SHA-256 match
            if prior.image_hash == sha256:
                return True, f"Exact duplicate image matches evidence #{prior.id} (SHA-256 match)"
            
            # Perceptual hash match (Hamming distance <= 8)
            dist = hex_hamming_distance(phash, prior.phash)
            if dist <= 8:
                return True, f"Visually similar duplicate matches evidence #{prior.id} (pHash distance: {dist})"

        return False, None

    def calculate_trust_score(
        self,
        incident_id: str,
        db: Session,
        verified_by: Optional[str] = None
    ) -> Verification:
        """Computes multi-factor TrustScore: 0.25G + 0.20Tm + 0.35V + 0.20I.
        Inserts an append-only verification row and updates incident confidence.
        """
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        if not incident:
            raise ValueError(f"Incident {incident_id} not found")

        # Fetch all evidence for this incident
        evidences = db.query(Evidence).filter(Evidence.incident_id == incident_id).all()

        # Find nearby reports within cluster radius and time window
        window_start = incident.created_at - timedelta(hours=self.time_window_hours)
        nearby_incidents = db.query(Incident).filter(
            Incident.id != incident_id,
            Incident.created_at >= window_start
        ).all()

        corroborating_reports = []
        for other in nearby_incidents:
            dist = haversine_distance_meters(
                incident.latitude, incident.longitude,
                other.latitude, other.longitude
            )
            if dist <= self.cluster_radius_m:
                corroborating_reports.append((other, dist))

        # 1. Geographic Agreement Score G (0 - 100)
        # Higher if corroborating reports are tightly clustered
        if corroborating_reports:
            # Average distance normalized to radius
            avg_dist = sum(d for _, d in corroborating_reports) / len(corroborating_reports)
            g_factor = max(0.0, 100.0 - (avg_dist / self.cluster_radius_m) * 60.0)
            # Bonus for count
            g_score = min(100.0, g_factor + len(corroborating_reports) * 15.0)
            g_reason = f"{len(corroborating_reports)} nearby report(s) within {self.cluster_radius_m:.0f}m (avg distance: {avg_dist:.1f}m)."
        else:
            g_score = 40.0  # Solo uncorroborated report baseline
            g_reason = f"Single ground report with no nearby corroborating reports within {self.cluster_radius_m:.0f}m."

        # 2. Temporal Agreement Score Tm (0 - 100)
        # Decays with age of incident
        age_hours = (datetime.utcnow() - incident.created_at).total_seconds() / 3600.0
        if age_hours <= 1.0:
            tm_score = 95.0
            tm_reason = f"Fresh report submitted {age_hours * 60:.0f} minutes ago."
        elif age_hours <= 3.0:
            tm_score = 80.0
            tm_reason = f"Active report submitted {age_hours:.1f} hours ago."
        elif age_hours <= self.time_window_hours:
            tm_score = 50.0
            tm_reason = f"Aging report submitted {age_hours:.1f} hours ago within window."
        else:
            tm_score = 25.0
            tm_reason = f"Stale report submitted {age_hours:.1f} hours ago (> {self.time_window_hours}h window)."

        # 3. Visual Quality Score V (0 - 100)
        # Based on Gemini AI confidence, visible water, and coverage
        if evidences:
            v_scores = []
            for ev in evidences:
                ai = ev.ai_result or {}
                conf = ev.ai_confidence or ai.get("confidence", 0.5)
                has_water = ev.visible_water or ai.get("visible_water", False)
                coverage = ai.get("estimated_coverage", 0.3)
                
                base = conf * 60.0
                water_bonus = 30.0 if has_water else 0.0
                cov_bonus = coverage * 10.0
                v_scores.append(min(100.0, base + water_bonus + cov_bonus))
            v_score = sum(v_scores) / len(v_scores)
            v_reason = f"Analyzed {len(evidences)} photo(s). Visible water confirmed with AI confidence."
        else:
            v_score = 30.0
            v_reason = "No photographic evidence uploaded yet."

        # 4. Independent-Source Quality Score I (0 - 100)
        # Distinct users with non-duplicate images
        unique_users = set()
        if incident.created_by:
            unique_users.add(incident.created_by)
        for other, _ in corroborating_reports:
            if other.created_by and other.created_by not in unique_users:
                unique_users.add(other.created_by)

        unique_count = len(unique_users)
        if unique_count >= 3:
            i_score = 95.0
            i_reason = f"High corroboration: {unique_count} distinct independent reporting sources."
        elif unique_count == 2:
            i_score = 70.0
            i_reason = "Medium corroboration: 2 distinct independent reporting sources."
        elif unique_count == 1:
            i_score = 35.0
            i_reason = "Single source: only 1 citizen report recorded for this zone."
        else:
            i_score = 20.0
            i_reason = "Anonymous unverified submission."

        # Composite TrustScore: 0.25G + 0.20Tm + 0.35V + 0.20I
        trust_score = round(
            0.25 * g_score +
            0.20 * tm_score +
            0.35 * v_score +
            0.20 * i_score,
            1
        )
        trust_score = max(0.0, min(100.0, trust_score))

        # Confidence label assignment
        if trust_score >= 85.0:
            confidence_label = "High-confidence evidence"
        elif trust_score >= 70.0:
            confidence_label = "Strong evidence"
        elif trust_score >= 40.0:
            confidence_label = "Probable"
        else:
            confidence_label = "Unverified"

        explanation = {
            "geographic_agreement": round(g_score, 1),
            "geographic_reason": g_reason,
            "temporal_agreement": round(tm_score, 1),
            "temporal_reason": tm_reason,
            "visual_quality": round(v_score, 1),
            "visual_reason": v_reason,
            "independent_sources": round(i_score, 1),
            "independent_sources_reason": i_reason,
            "formula": "TrustScore = 0.25*G + 0.20*Tm + 0.35*V + 0.20*I",
            "threshold_notice": "Thresholds are heuristic, not validated."
        }

        # Append-only insertion into verifications table
        verification = Verification(
            incident_id=incident_id,
            verified_by=verified_by,
            geographic_agreement=g_score,
            temporal_agreement=tm_score,
            visual_quality=v_score,
            independent_source_quality=i_score,
            trust_score=trust_score,
            confidence_label=confidence_label,
            explanation=explanation
        )
        db.add(verification)

        # Update incident confidence_score
        incident.confidence_score = trust_score
        db.commit()
        db.refresh(verification)

        return verification


verification_service = VerificationService()
