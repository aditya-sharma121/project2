"use client";

import React, { useState, useEffect } from "react";
import dynamic from "next/dynamic";
import { api, RouteResponse } from "@/lib/api";
import { DisclaimerBanner } from "@/components/DisclaimerBanner";

const LeafletMap = dynamic(
  () => import("@/components/LeafletMap").then((mod) => mod.LeafletMap),
  { ssr: false, loading: () => <div className="h-full flex items-center justify-center font-mono text-muted">Loading route canvas...</div> }
);

const PRESET_LOCATIONS = [
    { label: "Cantonment Station (South)", lat: 27.1700, lng: 78.0030 },
    { label: "Pratappura Crossing", lat: 27.1730, lng: 78.0050 },
    { label: "MG Road Central Corridor", lat: 27.1767, lng: 78.0081 },
    { label: "Civil Lines Bypass (West)", lat: 27.1780, lng: 78.0020 },
    { label: "St. John Junction", lat: 27.1800, lng: 78.0120 },
    { label: "North District Hospital", lat: 27.1850, lng: 78.0100 },
];

export default function RoutesPage() {
  const [originIndex, setOriginIndex] = useState(0);
  const [destIndex, setDestIndex] = useState(5);
  const [avoidRisk, setAvoidRisk] = useState(true);
  const [lambdaRisk, setLambdaRisk] = useState(5.0);

  const [calculating, setCalculating] = useState(false);
  const [routeResult, setRouteResult] = useState<any | null>(null);
  const [roads, setRoads] = useState<any[]>([]);

  useEffect(() => {
    // Load road segments for background
    api.getRoadRisksGeoJSON().then((geo: any) => {
      const mapped = (geo.features || []).map((f: any) => ({
        id: f.properties.id,
        name: f.properties.name,
        coordinates: f.geometry.coordinates,
        riskScore: f.properties.risk_score,
        riskLevel: f.properties.risk_level,
        isBlocked: f.properties.is_blocked,
      }));
      setRoads(mapped);
    }).catch(() => {});
  }, []);

  const handleCalculate = async () => {
    setCalculating(true);
    try {
      const orig = PRESET_LOCATIONS[originIndex];
      const dest = PRESET_LOCATIONS[destIndex];

      const res = await api.calculateRoute(
        { lat: orig.lat, lng: orig.lng },
        { lat: dest.lat, lng: dest.lng },
        avoidRisk
      );
      setRouteResult(res);
    } catch (e: any) {
      alert(`Routing calculation error: ${e.message}`);
    } finally {
      setCalculating(false);
    }
  };

  useEffect(() => {
    handleCalculate();
  }, [originIndex, destIndex, avoidRisk]);

  return (
    <div className="h-[calc(100vh-100px)] flex flex-col">
      <DisclaimerBanner className="rounded-none border-x-0" />

      <div className="flex-1 flex flex-col lg:flex-row overflow-hidden">
        {/* Left Control Drawer */}
        <div className="w-full lg:w-96 border-b lg:border-b-0 lg:border-r border-borderDark bg-surface p-5 flex flex-col space-y-5 overflow-y-auto">
          <div>
            <h2 className="text-xl font-bold tracking-tight">Hazard-Aware Routing</h2>
            <p className="text-xs text-muted font-mono mt-1">
              NetworkX Dijkstra engine with dynamic inundation penalties
            </p>
          </div>

          {/* Form */}
          <div className="space-y-4 text-xs font-mono">
            <div>
              <label className="text-muted uppercase block mb-1 font-semibold">Origin Point</label>
              <select
                value={originIndex}
                onChange={(e) => setOriginIndex(Number(e.target.value))}
                className="w-full bg-background border border-borderDark rounded px-3 py-2 text-foreground focus:border-primary"
              >
                {PRESET_LOCATIONS.map((loc, idx) => (
                  <option key={idx} value={idx}>{loc.label}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="text-muted uppercase block mb-1 font-semibold">Destination</label>
              <select
                value={destIndex}
                onChange={(e) => setDestIndex(Number(e.target.value))}
                className="w-full bg-background border border-borderDark rounded px-3 py-2 text-foreground focus:border-primary"
              >
                {PRESET_LOCATIONS.map((loc, idx) => (
                  <option key={idx} value={idx}>{loc.label}</option>
                ))}
              </select>
            </div>

            <div className="pt-2">
              <label className="flex items-center space-x-2 cursor-pointer p-2 rounded bg-background border border-borderDark">
                <input
                  type="checkbox"
                  checked={avoidRisk}
                  onChange={(e) => setAvoidRisk(e.target.checked)}
                  className="rounded bg-background border-borderDark text-primary"
                />
                <span className="font-semibold text-foreground">
                  Exclude High-Risk Roads (Risk &ge; 80 or Blocked)
                </span>
              </label>
            </div>

            <button
              onClick={handleCalculate}
              disabled={calculating}
              className="w-full py-2.5 rounded bg-primary text-background font-bold text-xs uppercase tracking-wider hover:bg-primary-light transition-all"
            >
              {calculating ? "Calculating Routes..." : "Recalculate Optimal Path"}
            </button>
          </div>

          {/* Route Comparison Stats */}
          {routeResult && (
            <div className="space-y-4 border-t border-borderDark pt-4 font-mono text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 rounded bg-background border border-borderDark">
                  <span className="text-[11px] text-muted block">Direct Shortest Route</span>
                  <div className="text-base font-bold text-muted mt-1">
                    {routeResult.standard_route ? `${routeResult.standard_route.distance_m} m` : "No Path"}
                  </div>
                  <span className="text-[10px] text-critical">
                    Hazard Risk: {routeResult.standard_route?.total_risk.toFixed(1) || 0}
                  </span>
                </div>

                <div className="p-3 rounded bg-background border border-primary/40">
                  <span className="text-[11px] text-primary font-semibold block">Risk-Aware Path</span>
                  <div className="text-base font-bold text-primary mt-1">
                    {routeResult.risk_aware_route ? `${routeResult.risk_aware_route.distance_m} m` : "No Path"}
                  </div>
                  <span className="text-[10px] text-success">
                    Hazard Risk: {routeResult.risk_aware_route?.total_risk.toFixed(1) || 0}
                  </span>
                </div>
              </div>

              {/* Detour stats */}
              <div className="p-3 rounded bg-surface border border-borderDark space-y-1 text-[11px]">
                <div className="flex justify-between">
                  <span className="text-muted">Detour Distance:</span>
                  <span className="text-foreground font-semibold">
                    +{routeResult.distance_difference_m > 0 ? routeResult.distance_difference_m : 0} m
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted">Hazard Exposure Reduction:</span>
                  <span className="text-success font-semibold">
                    {routeResult.risk_reduction_pct}% safer
                  </span>
                </div>
              </div>

              {/* Avoided Segments List */}
              {routeResult.avoided_segments && routeResult.avoided_segments.length > 0 && (
                <div className="space-y-2">
                  <span className="text-warning font-semibold uppercase block">
                    Avoided Hazardous Segments ({routeResult.avoided_segments.length})
                  </span>
                  <div className="space-y-1.5 max-h-40 overflow-y-auto">
                    {routeResult.avoided_segments.map((seg: any, idx: number) => (
                      <div key={idx} className="p-2 rounded bg-background border border-critical/30 text-[11px]">
                        <div className="text-critical font-bold">{seg.name || seg.segment_id}</div>
                        <div className="text-muted">{seg.reason}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Right Map Viewport */}
        <div className="flex-1 bg-background relative h-full">
          <LeafletMap
            roads={roads}
            routeCoordinates={routeResult?.risk_aware_route?.coordinates}
            standardRouteCoordinates={routeResult?.standard_route?.coordinates}
            center={[27.1767, 78.0081]}
            zoom={14}
          />
        </div>
      </div>
    </div>
  );
}
