from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.incident import Incident
from app.models.road_segment import RoadSegment


class GeospatialService:
    def incidents_to_geojson(self, incidents: List[Incident]) -> Dict[str, Any]:
        """Convert incidents to GeoJSON FeatureCollection with severity, confidence, freshness, is_simulated."""
        now = datetime.utcnow()
        features = []
        for inc in incidents:
            age_minutes = round((now - inc.created_at).total_seconds() / 60.0, 1)
            is_stale = age_minutes > 360.0  # > 6 hours is stale

            feature = {
                "type": "Feature",
                "id": inc.id,
                "geometry": {
                    "type": "Point",
                    "coordinates": [inc.longitude, inc.latitude]
                },
                "properties": {
                    "id": inc.id,
                    "title": inc.title,
                    "description": inc.description,
                    "reported_severity": inc.reported_severity,
                    "ai_severity": inc.ai_severity,
                    "status": inc.status,
                    "confidence_score": inc.confidence_score,
                    "risk_score": inc.risk_score,
                    "is_simulated": inc.is_simulated,
                    "freshness_minutes": age_minutes,
                    "is_stale": is_stale,
                    "created_at": inc.created_at.isoformat()
                }
            }
            features.append(feature)

        return {
            "type": "FeatureCollection",
            "features": features
        }

    def road_risks_to_geojson(self, road_segments: List[RoadSegment]) -> Dict[str, Any]:
        """Convert road segments to GeoJSON FeatureCollection."""
        features = []
        for road in road_segments:
            # Synthetic coordinate coordinates between start_node and end_node for demonstration
            # Agra grid coordinate mapping:
            coords = self._get_segment_coordinates(road.start_node, road.end_node)
            feature = {
                "type": "Feature",
                "id": road.id,
                "geometry": {
                    "type": "LineString",
                    "coordinates": coords
                },
                "properties": {
                    "id": road.id,
                    "external_id": road.external_id,
                    "name": road.name or f"Segment {road.external_id}",
                    "road_class": road.road_class,
                    "start_node": road.start_node,
                    "end_node": road.end_node,
                    "distance_m": road.distance_m,
                    "risk_score": road.risk_score,
                    "risk_level": road.risk_level,
                    "is_blocked": road.is_blocked
                }
            }
            features.append(feature)

        return {
            "type": "FeatureCollection",
            "features": features
        }

    def _get_segment_coordinates(self, start: str, end: str) -> List[List[float]]:
        # Predefined node coordinates around Agra (Lat 27.1767, Lng 78.0081)
        nodes = {
            "node_1": [78.0050, 27.1730],
            "node_2": [78.0081, 27.1767],
            "node_3": [78.0120, 27.1800],
            "node_4": [78.0020, 27.1780],
            "node_5": [78.0150, 27.1750],
            "node_6": [78.0100, 27.1850],
        }
        pt1 = nodes.get(start, [78.0050, 27.1730])
        pt2 = nodes.get(end, [78.0120, 27.1800])
        return [pt1, pt2]


geospatial_service = GeospatialService()
