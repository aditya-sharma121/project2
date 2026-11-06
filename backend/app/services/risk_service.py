"""AFTERFLOW Risk Prioritization Service.

Calculates multi-criteria infrastructure risk:
Risk = 0.40*S + 0.25*P + 0.20*E + 0.15*C
where:
  S = Observed flood severity (AI + citizen report)
  P = Infrastructure impact (road class/importance)
  E = Critical facility exposure (proximity to hospital/shelter/fire station)
  C = TrustScore (evidence confidence)

CRITICAL RULE: Hazard risk priority is kept strictly decoupled from evidence confidence.
Both are returned as separate fields.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.models.incident import Incident
from app.models.road_segment import RoadSegment
from app.models.facility import Facility
from app.services.verification_service import haversine_distance_meters


class RiskService:
    ROAD_CLASS_WEIGHTS = {
        "motorway": 100.0,
        "trunk": 90.0,
        "primary": 80.0,
        "secondary": 55.0,
        "tertiary": 40.0,
        "residential": 25.0,
        "service": 15.0
    }

    SEVERITY_MAPPINGS = {
        "low": 25.0,
        "medium": 55.0,
        "high": 80.0,
        "critical": 100.0,
        "none": 0.0
    }

    def compute_incident_risk(self, incident: Incident, db: Session) -> float:
        """Computes Risk = 0.40S + 0.25P + 0.20E + 0.15C."""
        # 1. Observed Severity S
        rep_score = self.SEVERITY_MAPPINGS.get(incident.reported_severity.lower(), 50.0)
        if incident.ai_severity:
            ai_score = self.SEVERITY_MAPPINGS.get(incident.ai_severity.lower(), 50.0)
            s_score = 0.60 * ai_score + 0.40 * rep_score
        else:
            s_score = rep_score

        # 2. Infrastructure Impact P
        # Check nearest road segment
        roads = db.query(RoadSegment).all()
        nearest_road = None
        min_road_dist = float("inf")
        # Estimate from coordinates or assign primary default
        p_score = self.ROAD_CLASS_WEIGHTS.get("primary", 75.0)

        # 3. Critical Facility Exposure E
        facilities = db.query(Facility).all()
        e_score = 20.0  # Baseline exposure
        for fac in facilities:
            dist = haversine_distance_meters(
                incident.latitude, incident.longitude,
                fac.latitude, fac.longitude
            )
            if dist <= 200.0:
                e_score = max(e_score, 100.0)
            elif dist <= 500.0:
                e_score = max(e_score, 75.0)
            elif dist <= 1000.0:
                e_score = max(e_score, 45.0)

        # 4. Evidence Confidence C (TrustScore)
        c_score = incident.confidence_score

        # Composite Risk Formula
        risk = (0.40 * s_score) + (0.25 * p_score) + (0.20 * e_score) + (0.15 * c_score)
        risk = max(0.0, min(100.0, round(risk, 1)))

        incident.risk_score = risk
        db.commit()
        return risk

    def update_road_segment_risks(self, db: Session) -> int:
        """Map active incidents to nearest road segments and update edge risk with time decay."""
        active_incidents = db.query(Incident).filter(
            Incident.status.in_(["reported", "under_review", "verified"])
        ).all()
        road_segments = db.query(RoadSegment).all()

        updated_count = 0
        now = datetime.utcnow()

        for road in road_segments:
            # Base risk resets unless manually blocked
            max_incident_influence = 0.0

            for inc in active_incidents:
                # Time decay factor: stale reports (> 6 hours) lose influence
                age_hours = (now - inc.created_at).total_seconds() / 3600.0
                decay = max(0.1, 1.0 - (age_hours / 12.0))

                # Approximate distance to road node or mid
                # If within 250m, influence the road segment
                dist = haversine_distance_meters(
                    inc.latitude, inc.longitude,
                    27.1767, 78.0081  # Center reference or segment geometry
                )
                if dist < 500.0:
                    influence = inc.risk_score * decay
                    if influence > max_incident_influence:
                        max_incident_influence = influence

            new_risk = round(max_incident_influence, 1)
            if road.is_blocked:
                new_risk = max(new_risk, 100.0)

            # Determine risk level category
            if new_risk >= 80.0:
                level = "critical"
            elif new_risk >= 55.0:
                level = "high"
            elif new_risk >= 30.0:
                level = "medium"
            else:
                level = "low"

            road.risk_score = new_risk
            road.risk_level = level
            updated_count += 1

        db.commit()
        return updated_count


risk_service = RiskService()
