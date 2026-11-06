"""AFTERFLOW NetworkX Dijkstra Hazard-Aware Routing Engine.

Computes safe paths around urban flood inundation zones.
Cost function:
  Edge_Cost = Distance_m + (lambda_risk * Risk_Score)
Excluded edges:
  is_blocked == True OR Risk_Score >= 80.0
"""

import time
import math
import logging
from datetime import datetime
from typing import Dict, Any, List, Tuple, Optional
import networkx as nx

from app.config import settings
from app.services.verification_service import haversine_distance_meters
from app.schemas.route import RouteCalculateResponse, RoutePath, AvoidedEdge, LatLng

logger = logging.getLogger("afterflow.routing")

# Agra City Seed Network Nodes (Center: 27.1767, 78.0081)
AGRA_NODES = {
    "node_1": {"lat": 27.1730, "lng": 78.0050, "name": "Pratappura Crossing"},
    "node_2": {"lat": 27.1767, "lng": 78.0081, "name": "MG Road Central"},
    "node_3": {"lat": 27.1800, "lng": 78.0120, "name": "St. John's Junction"},
    "node_4": {"lat": 27.1780, "lng": 78.0020, "name": "Civil Lines Bypass West"},
    "node_5": {"lat": 27.1750, "lng": 78.0150, "name": "Fatehabad Road East"},
    "node_6": {"lat": 27.1850, "lng": 78.0100, "name": "North District Hospital"},
    "node_7": {"lat": 27.1700, "lng": 78.0030, "name": "Cantonment Station South"},
    "node_8": {"lat": 27.1820, "lng": 78.0050, "name": "Raja Ki Mandi Station"},
}

# Predefined road segments with alternative bypass routes
# Node 1 -> Node 2 -> Node 3 -> Node 6 is the direct main corridor (MG Road)
# Node 1 -> Node 4 -> Node 8 -> Node 6 is the western elevated bypass
# Node 1 -> Node 5 -> Node 3 -> Node 6 is the eastern corridor
DEFAULT_EDGES = [
    {"id": "seg_1_2", "u": "node_1", "v": "node_2", "name": "MG Road South", "distance_m": 550.0, "risk_score": 0.0, "is_blocked": False},
    {"id": "seg_2_3", "u": "node_2", "v": "node_3", "name": "MG Road Central", "distance_m": 600.0, "risk_score": 0.0, "is_blocked": False},
    {"id": "seg_3_6", "u": "node_3", "v": "node_6", "name": "Hospital Link North", "distance_m": 700.0, "risk_score": 0.0, "is_blocked": False},
    {"id": "seg_1_4", "u": "node_1", "v": "node_4", "name": "Civil Lines West Way", "distance_m": 650.0, "risk_score": 0.0, "is_blocked": False},
    {"id": "seg_4_8", "u": "node_4", "v": "node_8", "name": "Bypass Elevated Link", "distance_m": 600.0, "risk_score": 0.0, "is_blocked": False},
    {"id": "seg_8_6", "u": "node_8", "v": "node_6", "name": "North Gate Access", "distance_m": 650.0, "risk_score": 0.0, "is_blocked": False},
    {"id": "seg_1_5", "u": "node_1", "v": "node_5", "name": "Fatehabad Link", "distance_m": 800.0, "risk_score": 0.0, "is_blocked": False},
    {"id": "seg_5_3", "u": "node_5", "v": "node_3", "name": "Bazaar Crossing", "distance_m": 750.0, "risk_score": 0.0, "is_blocked": False},
    {"id": "seg_2_4", "u": "node_2", "v": "node_4", "name": "Cross Connector West", "distance_m": 500.0, "risk_score": 0.0, "is_blocked": False},
    {"id": "seg_4_3", "u": "node_4", "v": "node_3", "name": "Diagonal Bypass", "distance_m": 700.0, "risk_score": 0.0, "is_blocked": False},
]


class RoutingEngine:
    def __init__(self, lambda_risk: float = settings.ROUTING_LAMBDA):
        self.lambda_risk = lambda_risk
        self.nodes = AGRA_NODES
        self.graph = nx.Graph()
        self._initialize_graph()

    def _initialize_graph(self):
        """Constructs in-memory graph from local cached network."""
        self.graph.clear()
        for node_id, data in self.nodes.items():
            self.graph.add_node(node_id, lat=data["lat"], lng=data["lng"], name=data["name"])

        for edge in DEFAULT_EDGES:
            self.graph.add_edge(
                edge["u"],
                edge["v"],
                id=edge["id"],
                name=edge["name"],
                distance_m=edge["distance_m"],
                risk_score=edge["risk_score"],
                is_blocked=edge["is_blocked"]
            )
        logger.info(f"Local routing graph initialized: {len(self.graph.nodes)} nodes, {len(self.graph.edges)} edges.")

    def update_edge_risk(self, segment_id: str, risk_score: float, is_blocked: bool = False):
        """Update risk score or blockage for a given segment in memory."""
        for u, v, data in self.graph.edges(data=True):
            if data.get("id") == segment_id:
                data["risk_score"] = risk_score
                data["is_blocked"] = is_blocked
                logger.info(f"Edge {segment_id} updated: risk={risk_score}, blocked={is_blocked}")
                break

    def snap_to_nearest_node(self, lat: float, lng: float) -> str:
        """Find closest intersection node to given coordinate."""
        nearest_node = None
        min_dist = float("inf")
        for node_id, data in self.nodes.items():
            dist = haversine_distance_meters(lat, lng, data["lat"], data["lng"])
            if dist < min_dist:
                min_dist = dist
                nearest_node = node_id
        return nearest_node or "node_1"

    def _build_route_path(self, node_list: List[str], graph: nx.Graph) -> RoutePath:
        coords = []
        total_dist = 0.0
        total_risk = 0.0

        for i in range(len(node_list)):
            n_curr = node_list[i]
            nd = self.nodes[n_curr]
            coords.append([nd["lng"], nd["lat"]])

            if i > 0:
                n_prev = node_list[i - 1]
                edge_data = graph.get_edge_data(n_prev, n_curr)
                if edge_data:
                    total_dist += edge_data.get("distance_m", 100.0)
                    total_risk += edge_data.get("risk_score", 0.0)

        # Average walking/driving estimated duration (avg speed 25 km/h in wet conditions)
        duration_sec = round((total_dist / (25.0 * 1000.0 / 3600.0)), 1)

        geometry = {
            "type": "LineString",
            "coordinates": coords
        }

        return RoutePath(
            nodes=node_list,
            coordinates=coords,
            distance_m=round(total_dist, 1),
            total_risk=round(total_risk, 1),
            estimated_duration_sec=duration_sec,
            geometry=geometry
        )

    def calculate_routes(
        self,
        origin: LatLng,
        destination: LatLng,
        avoid_high_risk: bool = True,
        lambda_val: Optional[float] = None
    ) -> RouteCalculateResponse:
        """Computes both standard shortest path and risk-aware route."""
        l_risk = lambda_val if lambda_val is not None else self.lambda_risk
        start_node = self.snap_to_nearest_node(origin.lat, origin.lng)
        end_node = self.snap_to_nearest_node(destination.lat, destination.lng)

        if start_node == end_node:
            # Shift end_node if identical
            end_node = "node_6" if start_node != "node_6" else "node_1"

        # 1. Plain shortest route (Dijkstra on distance only)
        standard_path_nodes = []
        try:
            standard_path_nodes = nx.dijkstra_path(
                self.graph,
                source=start_node,
                target=end_node,
                weight="distance_m"
            )
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            standard_path_nodes = []

        standard_route = self._build_route_path(standard_path_nodes, self.graph) if standard_path_nodes else None

        # 2. Risk-aware route
        # Create subgraph excluding blocked edges and edges with risk >= 80
        risk_subgraph = nx.Graph()
        for n, d in self.graph.nodes(data=True):
            risk_subgraph.add_node(n, **d)

        avoided_edges: List[AvoidedEdge] = []

        for u, v, data in self.graph.edges(data=True):
            risk = data.get("risk_score", 0.0)
            blocked = data.get("is_blocked", False)

            if avoid_high_risk and (blocked or risk >= 80.0):
                reason = "Blocked by operator order" if blocked else f"Severe flood hazard risk ({risk:.1f}/100 >= 80)"
                avoided_edges.append(AvoidedEdge(
                    edge=[u, v],
                    segment_id=data.get("id"),
                    name=data.get("name"),
                    risk_score=risk,
                    reason=reason
                ))
            else:
                # Cost = distance + lambda * risk
                hazard_cost = data.get("distance_m", 100.0) + (l_risk * risk)
                risk_subgraph.add_edge(u, v, **data, cost=hazard_cost)

        risk_aware_nodes = []
        try:
            risk_aware_nodes = nx.dijkstra_path(
                risk_subgraph,
                source=start_node,
                target=end_node,
                weight="cost"
            )
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            risk_aware_nodes = []

        risk_route = self._build_route_path(risk_aware_nodes, self.graph) if risk_aware_nodes else None

        # Stats comparison
        dist_diff = 0.0
        risk_reduct = 0.0
        if standard_route and risk_route:
            dist_diff = round(risk_route.distance_m - standard_route.distance_m, 1)
            if standard_route.total_risk > 0:
                risk_reduct = round(((standard_route.total_risk - risk_route.total_risk) / standard_route.total_risk) * 100.0, 1)

        return RouteCalculateResponse(
            standard_route=standard_route,
            risk_aware_route=risk_route,
            avoided_segments=avoided_edges,
            distance_difference_m=dist_diff,
            risk_reduction_pct=risk_reduct,
            computed_at=datetime.utcnow().isoformat(),
            disclaimer="AFTERFLOW is an advisory decision-support prototype. Routes are not guaranteed safe. Always follow official directives."
        )


routing_engine = RoutingEngine()
