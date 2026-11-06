"""AFTERFLOW Agra Road Graph Network Seeder."""
import sys
import os
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), "..")))

from app.database.connection import SessionLocal
from app.models.road_segment import RoadSegment
from app.services.routing_service import DEFAULT_EDGES


def seed_road_graph():
    db = SessionLocal()
    try:
        print("Seeding Agra urban road network graph segments...")
        count = 0
        for edge in DEFAULT_EDGES:
            existing = db.query(RoadSegment).filter(RoadSegment.external_id == edge["id"]).first()
            if not existing:
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
                count += 1
        db.commit()
        print(f"Successfully seeded {count} road segments.")
    finally:
        db.close()


if __name__ == "__main__":
    seed_road_graph()
