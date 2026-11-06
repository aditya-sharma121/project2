"use client";

import React, { useState, useEffect } from "react";
import dynamic from "next/dynamic";
import { api } from "@/lib/api";
import { useIncidentsSocket, WsEvent } from "@/lib/useIncidentsSocket";
import { DisclaimerBanner } from "@/components/DisclaimerBanner";

// Dynamically import Leaflet with SSR disabled
const LeafletMap = dynamic(
  () => import("@/components/LeafletMap").then((mod) => mod.LeafletMap),
  { ssr: false, loading: () => <div className="h-full flex items-center justify-center font-mono text-muted">Loading Leaflet OSM viewport...</div> }
);

export default function MapPage() {
  const [incidents, setIncidents] = useState<any[]>([]);
  const [roads, setRoads] = useState<any[]>([]);
  const [facilities, setFacilities] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // Filter states
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [severityFilter, setSeverityFilter] = useState<string>("all");
  const [minConfidence, setMinConfidence] = useState<number>(0);
  const [hideSimulated, setHideSimulated] = useState<boolean>(false);

  // Layer toggles
  const [showIncidents, setShowIncidents] = useState<boolean>(true);
  const [showRoads, setShowRoads] = useState<boolean>(true);
  const [showFacilities, setShowFacilities] = useState<boolean>(true);

  const fetchData = async () => {
    try {
      setLoading(true);
      // Fetch incidents list
      const incRes = await api.getIncidents({ limit: 100 });
      setIncidents(incRes.items || []);

      // Fetch road risks
      const roadGeo = await api.getRoadRisksGeoJSON();
      const mappedRoads = (roadGeo.features || []).map((f: any) => ({
        id: f.properties.id,
        name: f.properties.name,
        coordinates: f.geometry.coordinates,
        riskScore: f.properties.risk_score,
        riskLevel: f.properties.risk_level,
        isBlocked: f.properties.is_blocked,
      }));
      setRoads(mappedRoads);

      // Fetch facilities
      const facRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/facilities/nearby?lat=27.1767&lng=78.0081&radius_m=10000`);
      if (facRes.ok) {
        const facList = await facRes.json();
        setFacilities(
          facList.map((fc: any) => ({
            id: fc.id,
            name: fc.name,
            type: fc.facility_type,
            lat: fc.latitude,
            lng: fc.longitude,
          }))
        );
      }
    } catch {
      // Graceful fallback
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Live WebSocket updates
  const handleWsEvent = (event: WsEvent) => {
    if (
      event.event === "incident.created" ||
      event.event === "incident.status_changed" ||
      event.event === "route.hazard_updated"
    ) {
      fetchData();
    }
  };

  const { isConnected } = useIncidentsSocket(handleWsEvent);

  // Filtered incidents
  const filteredIncidents = incidents
    .filter((inc) => {
      if (statusFilter !== "all" && inc.status !== statusFilter) return false;
      if (severityFilter !== "all" && inc.reported_severity !== severityFilter) return false;
      if (inc.confidence_score < minConfidence) return false;
      if (hideSimulated && inc.is_simulated) return false;
      return true;
    })
    .map((inc) => ({
      id: inc.id,
      lat: inc.latitude,
      lng: inc.longitude,
      title: inc.title,
      severity: inc.reported_severity,
      confidence: inc.confidence_score,
      status: inc.status,
      isSimulated: inc.is_simulated,
      freshnessMin: inc.freshness_minutes,
    }));

  return (
    <div className="h-[calc(100vh-100px)] flex flex-col">
      <DisclaimerBanner className="rounded-none border-x-0" />

      <div className="flex-1 flex flex-col lg:flex-row overflow-hidden">
        {/* Left Control Drawer */}
        <div className="w-full lg:w-80 border-b lg:border-b-0 lg:border-r border-borderDark bg-surface p-4 flex flex-col space-y-4 overflow-y-auto">
          <div className="flex items-center justify-between border-b border-borderDark pb-2">
            <h2 className="font-bold text-base">Hazard Layers</h2>
            <div className="flex items-center gap-1.5 text-xs font-mono">
              <span className={`w-2 h-2 rounded-full ${isConnected ? "bg-success animate-pulse" : "bg-muted"}`}></span>
              <span className={isConnected ? "text-success" : "text-muted"}>
                {isConnected ? "LIVE TELEMETRY" : "OFFLINE"}
              </span>
            </div>
          </div>

          {/* Layer toggles */}
          <div className="space-y-2 text-xs font-mono">
            <label className="flex items-center space-x-2 cursor-pointer">
              <input
                type="checkbox"
                checked={showIncidents}
                onChange={(e) => setShowIncidents(e.target.checked)}
                className="rounded bg-background border-borderDark text-primary"
              />
              <span>Flood Incident Markers ({filteredIncidents.length})</span>
            </label>
            <label className="flex items-center space-x-2 cursor-pointer">
              <input
                type="checkbox"
                checked={showRoads}
                onChange={(e) => setShowRoads(e.target.checked)}
                className="rounded bg-background border-borderDark text-primary"
              />
              <span>Road Inundation Polylines ({roads.length})</span>
            </label>
            <label className="flex items-center space-x-2 cursor-pointer">
              <input
                type="checkbox"
                checked={showFacilities}
                onChange={(e) => setShowFacilities(e.target.checked)}
                className="rounded bg-background border-borderDark text-primary"
              />
              <span>Critical Facilities ({facilities.length})</span>
            </label>
          </div>

          <div className="border-t border-borderDark pt-3 space-y-3 text-xs font-mono">
            <span className="text-muted uppercase block font-semibold">Incident Filters</span>

            <div>
              <label className="text-muted block mb-1">Status</label>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="w-full bg-background border border-borderDark rounded px-2 py-1.5 focus:border-primary text-xs"
              >
                <option value="all">All Statuses</option>
                <option value="reported">Reported</option>
                <option value="under_review">Under Review</option>
                <option value="verified">Verified</option>
                <option value="resolved">Resolved</option>
              </select>
            </div>

            <div>
              <label className="text-muted block mb-1">Severity</label>
              <select
                value={severityFilter}
                onChange={(e) => setSeverityFilter(e.target.value)}
                className="w-full bg-background border border-borderDark rounded px-2 py-1.5 focus:border-primary text-xs"
              >
                <option value="all">All Severities</option>
                <option value="critical">Critical</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>
            </div>

            <div>
              <div className="flex justify-between text-muted mb-1">
                <span>Min TrustScore</span>
                <span>{minConfidence}+</span>
              </div>
              <input
                type="range"
                min="0"
                max="90"
                step="10"
                value={minConfidence}
                onChange={(e) => setMinConfidence(Number(e.target.value))}
                className="w-full accent-primary"
              />
            </div>

            <label className="flex items-center space-x-2 cursor-pointer">
              <input
                type="checkbox"
                checked={hideSimulated}
                onChange={(e) => setHideSimulated(e.target.checked)}
                className="rounded bg-background border-borderDark text-primary"
              />
              <span>Hide Simulated Incidents</span>
            </label>
          </div>

          {/* Map Legend */}
          <div className="border-t border-borderDark pt-3 space-y-2 text-[11px] font-mono text-muted">
            <span className="uppercase text-foreground font-semibold block">Map Legend</span>
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-critical"></span>
              <span>High / Critical Inundation</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-warning"></span>
              <span>Medium Waterlogging</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-success"></span>
              <span>Passable / Low Risk</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-4 h-0.5 border-t-2 border-dashed border-critical"></span>
              <span>Blocked Segment (Dijkstra excluded)</span>
            </div>
          </div>
        </div>

        {/* Right Map Viewport */}
        <div className="flex-1 bg-background relative h-full">
          <LeafletMap
            incidents={showIncidents ? filteredIncidents : []}
            roads={showRoads ? roads : []}
            facilities={showFacilities ? facilities : []}
            center={[27.1767, 78.0081]}
            zoom={14}
          />
        </div>
      </div>
    </div>
  );
}
