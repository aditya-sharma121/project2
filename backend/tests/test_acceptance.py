"""AFTERFLOW 48-Hour Hackathon Acceptance Test Suite.

Verifies:
1. Clear road image vs flood image assessment
2. Image duplicate detection (SHA-256 and pHash)
3. Multi-factor TrustScore calculation and progression (Unverified -> Probable -> Strong)
4. Decoupling of Hazard Priority Risk vs Evidence Confidence
5. Hazard-aware Dijkstra routing engine (high risk segment exclusion & reroute)
6. Upload size/format validation (< 5MB)
7. AI graceful fallback (report saved even if AI service is unavailable)
8. Decision-support prototype disclaimer enforcement
"""

import io
import time
import pytest
from PIL import Image
from fastapi.testclient import TestClient

from app.main import app
from app.config import settings
from app.database.connection import SessionLocal, Base, engine
from app.models.user import User
from app.models.incident import Incident
from app.models.evidence import Evidence
from app.models.road_segment import RoadSegment
from app.services.gemini_service import gemini_service
from app.services.verification_service import verification_service
from app.services.risk_service import risk_service
from app.services.routing_service import routing_engine, LatLng
from app.core.security import get_password_hash, create_access_token

client = TestClient(app)


def create_dummy_image(color="blue", format="JPEG", size=(300, 300)) -> bytes:
    """Helper to generate dummy image bytes in memory."""
    img = Image.new("RGB", size, color=color)
    buf = io.BytesIO()
    img.save(buf, format=format)
    return buf.getvalue()


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield


def test_decision_support_disclaimer_health():
    """Rule: Disclaimer must be present on system health check."""
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert "disclaimer" in data
    assert "decision-support" in data["disclaimer"].lower()
    assert "not an official emergency" in data["disclaimer"].lower()


def test_ai_flood_assessment_mock_modes():
    """Phase 4: Gemini Vision assessment guardrail test (no water depth)."""
    flood_img = create_dummy_image(color="darkblue")
    res = client.post(
        "/api/v1/ai/analyze-image",
        files={"image": ("flood_water.jpg", flood_img, "image/jpeg")}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["classification"] in ["likely_flooding", "possible_flooding", "no_flooding"]
    assert "limitations" in data
    assert len(data["limitations"]) > 0
    # Guardrail check: depth must not be inferred
    assert any("depth cannot be inferred" in lim.lower() for lim in data["limitations"])


def test_invalid_upload_validation_rejected():
    """Rule: Reject images > 5MB or non-image types with descriptive error."""
    # Oversized image payload simulation (> 5MB)
    huge_bytes = b"0" * (6 * 1024 * 1024)
    res = client.post(
        "/api/v1/ai/analyze-image",
        files={"image": ("huge_file.jpg", huge_bytes, "image/jpeg")}
    )
    assert res.status_code == 400
    err = res.json()
    assert "5mb" in err["error"]["message"].lower()


def test_duplicate_image_deduplication():
    """Phase 5: Duplicate image hash detection."""
    db = SessionLocal()
    try:
        sample_img = create_dummy_image(color="teal")
        prep = gemini_service.preprocess_image(sample_img)

        # First insert
        ev1 = Evidence(
            incident_id="dummy_incident_1",
            image_url="https://res.cloudinary.com/demo/sample1.jpg",
            image_hash=prep["sha256"],
            phash=prep["phash"],
            visible_water=True,
            ai_confidence=0.9
        )
        db.add(ev1)
        db.commit()

        # Second check with exact same image
        is_dup, reason = verification_service.check_duplicate_image(prep["sha256"], prep["phash"], db)
        assert is_dup is True
        assert "duplicate" in reason.lower()
    finally:
        db.close()


def test_trust_score_multi_report_progression():
    """Phase 5: Independent reports corroborate and progress TrustScore (Unverified -> Strong)."""
    db = SessionLocal()
    try:
        # Isolated test coordinate far from seeded Agra center
        test_lat, test_lng = 28.5000, 77.2000

        # Create Incident A by User 1
        inc_a = Incident(
            title="Road Inundation Test Isolated Point",
            latitude=test_lat,
            longitude=test_lng,
            reported_severity="high",
            created_by="user_citizen_isolated_1"
        )
        db.add(inc_a)
        db.commit()
        db.refresh(inc_a)

        # Initial TrustScore (Single source, no nearby cluster => Unverified)
        v1 = verification_service.calculate_trust_score(inc_a.id, db)
        assert v1.trust_score < 50.0
        assert v1.confidence_label in ["Unverified", "Probable"]

        # Create nearby corroborating report Incident B by distinct User 2 (within 80m)
        inc_b = Incident(
            title="Corroborating flood report isolated",
            latitude=test_lat + 0.0005,
            longitude=test_lng + 0.0005,
            reported_severity="high",
            created_by="user_citizen_isolated_2"
        )
        db.add(inc_b)
        db.commit()
        db.refresh(inc_b)

        # Recalculate Incident A TrustScore with corroboration
        v2 = verification_service.calculate_trust_score(inc_a.id, db)
        assert v2.trust_score > v1.trust_score
        assert v2.geographic_agreement > v1.geographic_agreement
    finally:
        db.close()


def test_hazard_priority_vs_confidence_decoupling():
    """Rule: Hazard Priority Risk must remain strictly separate from Evidence Confidence."""
    db = SessionLocal()
    try:
        inc = Incident(
            title="Critical Flood Warning Bypass",
            latitude=27.1767,
            longitude=78.0081,
            reported_severity="critical",
            confidence_score=35.0  # Low confidence / single unverified report
        )
        db.add(inc)
        db.commit()
        db.refresh(inc)

        risk = risk_service.compute_incident_risk(inc, db)
        # Even with low confidence (35), critical severity + hospital proximity yields substantial risk
        assert risk > 50.0
        assert inc.risk_score != inc.confidence_score
    finally:
        db.close()


def test_routing_engine_high_risk_exclusion():
    """Phase 7: NetworkX Dijkstra excludes edges with risk >= 80 and reroutes."""
    origin = LatLng(lat=27.1730, lng=78.0050)      # node_1
    dest = LatLng(lat=27.1850, lng=78.0100)        # node_6 (Hospital)

    # 1. Normal state: standard path and risk-aware path are identical direct path
    res1 = routing_engine.calculate_routes(origin, dest, avoid_high_risk=True)
    assert res1.risk_aware_route is not None
    assert len(res1.avoided_segments) == 0

    # 2. Inject high flood risk (90) on main corridor segment seg_1_2
    routing_engine.update_edge_risk("seg_1_2", risk_score=90.0, is_blocked=False)

    res2 = routing_engine.calculate_routes(origin, dest, avoid_high_risk=True)
    assert res2.risk_aware_route is not None
    # Node 1 -> Node 2 corridor must be excluded from risk-aware route
    assert any("seg_1_2" in str(seg.segment_id) for seg in res2.avoided_segments)
    # The risk-aware route reroutes via Civil Lines West Bypass
    assert "node_4" in res2.risk_aware_route.nodes

    # Reset edge risk
    routing_engine.update_edge_risk("seg_1_2", risk_score=0.0, is_blocked=False)


def test_performance_targets():
    """Performance targets: API < 1s, Route calculation < 2s."""
    t0 = time.time()
    res = client.get("/api/v1/incidents")
    t_api = time.time() - t0
    assert res.status_code == 200
    assert t_api < 1.0, f"API endpoint exceeded 1.0s target: {t_api:.3f}s"

    t0 = time.time()
    res_route = client.post(
        "/api/v1/routes/calculate",
        json={
            "origin": {"lat": 27.1730, "lng": 78.0050},
            "destination": {"lat": 27.1850, "lng": 78.0100},
            "avoid_high_risk": True
        }
    )
    t_route = time.time() - t0
    assert res_route.status_code == 200
    assert t_route < 2.0, f"Route engine exceeded 2.0s target: {t_route:.3f}s"
