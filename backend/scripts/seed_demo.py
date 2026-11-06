"""AFTERFLOW Demo Scenario Seeder.

Creates:
- 1 Operator account + 3 Citizen accounts
- 4 Critical Emergency Facilities (Hospital, Shelter, Fire Station)
- Agra road graph network with alternative corridors
- 3 Correlated flood reports near MG Road / St. John's Junction showing TrustScore progression:
    Report 1 (Citizen A): Unverified (Score ~35)
    Report 2 (Citizen B, 45m later): Probable (Score ~62)
    Report 3 (Citizen C, 1h later): Strong evidence (Score ~84)
- 1 Duplicate report attempt using identical image hash
- All synthetic entries marked with is_simulated=True.
"""

import sys
import os
import hashlib
from datetime import datetime, timedelta
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), "..")))

from app.database.connection import SessionLocal, Base, engine
from app.models.user import User
from app.models.incident import Incident
from app.models.evidence import Evidence
from app.models.verification import Verification
from app.models.facility import Facility
from app.models.road_segment import RoadSegment
from app.core.security import get_password_hash
from app.services.routing_service import DEFAULT_EDGES
from app.services.verification_service import verification_service
from app.services.risk_service import risk_service


def seed_demo_data():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        print("=== SEEDING AFTERFLOW HACKATHON DEMO ENVIRONMENT ===")

        # 1. Seed Users (1 Operator + 3 Citizens)
        users_data = [
            {"email": "operator@afterflow.gov", "password": "operatorpassword", "full_name": "Major R. Sharma (Disaster Cell)", "role": "operator"},
            {"email": "citizen1@agra.org", "password": "citizenpassword", "full_name": "Aarav Mehta (Citizen Reporter)", "role": "citizen"},
            {"email": "citizen2@agra.org", "password": "citizenpassword", "full_name": "Pooja Verma (Local Commuter)", "role": "citizen"},
            {"email": "citizen3@agra.org", "password": "citizenpassword", "full_name": "Vikram Singh (Shop Owner)", "role": "citizen"},
        ]

        user_instances = {}
        for u in users_data:
            existing = db.query(User).filter(User.email == u["email"]).first()
            if not existing:
                user = User(
                    email=u["email"],
                    hashed_password=get_password_hash(u["password"]),
                    full_name=u["full_name"],
                    role=u["role"]
                )
                db.add(user)
                db.commit()
                db.refresh(user)
                user_instances[u["email"]] = user
            else:
                user_instances[u["email"]] = existing
        print(f"Users initialized: 1 Operator ({user_instances['operator@afterflow.gov'].email}), 3 Citizens.")

        # 2. Seed Critical Facilities
        facilities_data = [
            {"name": "District Emergency Hospital", "facility_type": "hospital", "lat": 27.1850, "lng": 78.0100, "capacity": 250},
            {"name": "Municipal Central Flood Shelter", "facility_type": "shelter", "lat": 27.1740, "lng": 78.0140, "capacity": 500},
            {"name": "City Fire & Rescue Station #4", "facility_type": "fire_station", "lat": 27.1720, "lng": 78.0040, "capacity": 40},
            {"name": "St. John Community Relief Center", "facility_type": "shelter", "lat": 27.1810, "lng": 78.0130, "capacity": 300},
        ]
        for f in facilities_data:
            if not db.query(Facility).filter(Facility.name == f["name"]).first():
                fac = Facility(
                    name=f["name"],
                    facility_type=f["facility_type"],
                    latitude=f["lat"],
                    longitude=f["lng"],
                    capacity=f["capacity"],
                    status="operational"
                )
                db.add(fac)
        db.commit()
        print(f"Critical facilities seeded.")

        # 3. Seed Road Network Segments
        for edge in DEFAULT_EDGES:
            if not db.query(RoadSegment).filter(RoadSegment.external_id == edge["id"]).first():
                seg = RoadSegment(
                    external_id=edge["id"],
                    name=edge["name"],
                    start_node=edge["u"],
                    end_node=edge["v"],
                    distance_m=edge["distance_m"],
                    risk_score=edge["risk_score"],
                    risk_level="low",
                    is_blocked=edge["is_blocked"]
                )
                db.add(seg)
        db.commit()
        print(f"Road segments seeded.")

        # 4. Seed Correlated Reports Progression
        # Epicenter around MG Road (Lat 27.1767, Lng 78.0081)
        base_time = datetime.utcnow() - timedelta(hours=2)

        # Image Hashes
        img_hash_1 = hashlib.sha256(b"flood_image_ground_evidence_1").hexdigest()
        img_hash_2 = hashlib.sha256(b"flood_image_ground_evidence_2").hexdigest()
        img_hash_3 = hashlib.sha256(b"flood_image_ground_evidence_3").hexdigest()

        # Report 1: Initial report by Citizen 1 (Standalone -> Unverified)
        inc1 = db.query(Incident).filter(Incident.title == "Simulated: Waterlogging near MG Road crossing").first()
        if not inc1:
            inc1 = Incident(
                title="Simulated: Waterlogging near MG Road crossing",
                description="Submerged road crossing, curb hidden by dirty water, 2 wheelers turning back.",
                incident_type="urban_flooding",
                reported_severity="medium",
                ai_severity="medium",
                status="reported",
                is_simulated=True,
                latitude=27.1767,
                longitude=78.0081,
                created_by=user_instances["citizen1@agra.org"].id,
                created_at=base_time
            )
            db.add(inc1)
            db.commit()
            db.refresh(inc1)

            ev1 = Evidence(
                incident_id=inc1.id,
                user_id=user_instances["citizen1@agra.org"].id,
                image_url="https://res.cloudinary.com/demo/image/upload/sample.jpg",
                image_hash=img_hash_1,
                phash="a1b2c3d4e5f60718",
                visible_water=True,
                ai_confidence=0.86,
                ai_result={
                    "classification": "likely_flooding",
                    "visible_water": True,
                    "severity": "medium",
                    "estimated_coverage": 0.55,
                    "confidence": 0.86,
                    "limitations": [
                        "Water depth cannot be inferred from 2D photographic perspective",
                        "Subsurface road craters not visible"
                    ]
                },
                is_duplicate=False,
                captured_at=base_time,
                uploaded_at=base_time
            )
            db.add(ev1)
            db.commit()

            # TrustScore calculation
            verification_service.calculate_trust_score(inc1.id, db, verified_by="system")
            risk_service.compute_incident_risk(inc1, db)
            print("Seeded Report 1 (Initial Citizen Report).")

        # Report 2: Corroborating report by Citizen 2 (45m later, 110m away -> Probable)
        inc2 = db.query(Incident).filter(Incident.title == "Simulated: Heavy standing water outside MG Road Market").first()
        if not inc2:
            time2 = base_time + timedelta(minutes=45)
            inc2 = Incident(
                title="Simulated: Heavy standing water outside MG Road Market",
                description="Water accumulated up to wheel hubs, slow crawl for light vehicles.",
                incident_type="urban_flooding",
                reported_severity="high",
                ai_severity="medium",
                status="reported",
                is_simulated=True,
                latitude=27.1774,
                longitude=78.0089,
                created_by=user_instances["citizen2@agra.org"].id,
                created_at=time2
            )
            db.add(inc2)
            db.commit()
            db.refresh(inc2)

            ev2 = Evidence(
                incident_id=inc2.id,
                user_id=user_instances["citizen2@agra.org"].id,
                image_url="https://res.cloudinary.com/demo/image/upload/sample.jpg",
                image_hash=img_hash_2,
                phash="b2c3d4e5f60718a9",
                visible_water=True,
                ai_confidence=0.91,
                ai_result={
                    "classification": "likely_flooding",
                    "visible_water": True,
                    "severity": "high",
                    "estimated_coverage": 0.75,
                    "confidence": 0.91,
                    "limitations": [
                        "Water depth cannot be inferred from 2D photographic perspective",
                        "Turbidity obscures depth profiling"
                    ]
                },
                is_duplicate=False,
                captured_at=time2,
                uploaded_at=time2
            )
            db.add(ev2)
            db.commit()

            verification_service.calculate_trust_score(inc2.id, db, verified_by="system")
            risk_service.compute_incident_risk(inc2, db)
            print("Seeded Report 2 (Independent Corroborating Report).")

        # Report 3: Third independent report by Citizen 3 (1h later, 90m away -> Strong evidence)
        inc3 = db.query(Incident).filter(Incident.title == "Simulated: Impassable flow near St. John junction").first()
        if not inc3:
            time3 = base_time + timedelta(hours=1, minutes=15)
            inc3 = Incident(
                title="Simulated: Impassable flow near St. John junction",
                description="Water rising rapidly, drains overflowing, small sedan stranded.",
                incident_type="urban_flooding",
                reported_severity="critical",
                ai_severity="high",
                status="verified",
                is_simulated=True,
                latitude=27.1779,
                longitude=78.0084,
                created_by=user_instances["citizen3@agra.org"].id,
                created_at=time3
            )
            db.add(inc3)
            db.commit()
            db.refresh(inc3)

            ev3 = Evidence(
                incident_id=inc3.id,
                user_id=user_instances["citizen3@agra.org"].id,
                image_url="https://res.cloudinary.com/demo/image/upload/sample.jpg",
                image_hash=img_hash_3,
                phash="c3d4e5f60718a9b2",
                visible_water=True,
                ai_confidence=0.94,
                ai_result={
                    "classification": "likely_flooding",
                    "visible_water": True,
                    "severity": "high",
                    "estimated_coverage": 0.85,
                    "confidence": 0.94,
                    "limitations": [
                        "Water depth cannot be inferred from 2D photographic perspective",
                        "Submerged hazards present"
                    ]
                },
                is_duplicate=False,
                captured_at=time3,
                uploaded_at=time3
            )
            db.add(ev3)
            db.commit()

            verification_service.calculate_trust_score(inc3.id, db, verified_by="operator")
            risk_service.compute_incident_risk(inc3, db)
            print("Seeded Report 3 (Third Independent Report -> High TrustScore).")

        # 5. Seed Duplicate Image Attempt Case
        inc_dup = db.query(Incident).filter(Incident.title == "Simulated: Duplicate photo re-upload test").first()
        if not inc_dup:
            time_dup = datetime.utcnow() - timedelta(minutes=10)
            inc_dup = Incident(
                title="Simulated: Duplicate photo re-upload test",
                description="Repetitive submission testing duplicate image deduplication engine.",
                incident_type="urban_flooding",
                reported_severity="medium",
                ai_severity="medium",
                status="reported",
                is_simulated=True,
                latitude=27.1765,
                longitude=78.0080,
                created_by=user_instances["citizen1@agra.org"].id,
                created_at=time_dup
            )
            db.add(inc_dup)
            db.commit()
            db.refresh(inc_dup)

            # Same hash as img_hash_1
            is_dup, reason = verification_service.check_duplicate_image(img_hash_1, "a1b2c3d4e5f60718", db)
            ev_dup = Evidence(
                incident_id=inc_dup.id,
                user_id=user_instances["citizen1@agra.org"].id,
                image_url="https://res.cloudinary.com/demo/image/upload/sample.jpg",
                image_hash=img_hash_1,
                phash="a1b2c3d4e5f60718",
                visible_water=True,
                ai_confidence=0.86,
                is_duplicate=is_dup,
                captured_at=time_dup,
                uploaded_at=time_dup
            )
            db.add(ev_dup)
            db.commit()
            verification_service.calculate_trust_score(inc_dup.id, db, verified_by="system")
            risk_service.compute_incident_risk(inc_dup, db)
            print(f"Seeded Duplicate Case (is_duplicate={is_dup}).")

        # Update road segment risks from active incidents
        risk_service.update_road_segment_risks(db)
        print("Road segment risks updated.")

        print("=== SEEDING COMPLETED SUCCESSFULLY ===")

    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_data()
