"use client";

import React, { useState, useEffect } from "react";
import { api } from "@/lib/api";
import { SeverityBadge } from "@/components/SeverityBadge";
import { ConfidenceBadge } from "@/components/ConfidenceBadge";
import { FreshnessLabel } from "@/components/FreshnessLabel";
import { SimulatedTag } from "@/components/SimulatedTag";
import { KpiCard } from "@/components/KpiCard";
import { DisclaimerBanner } from "@/components/DisclaimerBanner";
import { useIncidentsSocket, WsEvent } from "@/lib/useIncidentsSocket";

export default function OperatorDashboard() {
  const [kpis, setKpis] = useState<any>({
    active_incidents: 0,
    high_risk_incidents: 0,
    verified_incidents: 0,
    pending_review: 0,
    blocked_roads: 0,
    simulated_incidents: 0,
  });

  const [incidents, setIncidents] = useState<any[]>([]);
  const [timeline, setTimeline] = useState<any[]>([]);
  const [weather, setWeather] = useState<any | null>(null);
  const [roads, setRoads] = useState<any[]>([]);
  const [selectedIncident, setSelectedIncident] = useState<any | null>(null);
  const [explainability, setExplainability] = useState<any | null>(null);

  const [loading, setLoading] = useState(true);

  const loadDashboardData = async () => {
    try {
      setLoading(true);

      // KPIs
      const kpiData = await api.getDashboardKpis();
      setKpis(kpiData);

      // Incident Queue sorted by priority risk
      const incRes = await api.getIncidents({ limit: 50 });
      setIncidents(incRes.items || []);
      if (incRes.items && incRes.items.length > 0 && !selectedIncident) {
        setSelectedIncident(incRes.items[0]);
      }

      // Timeline events
      const tlRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/dashboard/timeline`);
      if (tlRes.ok) {
        const tlData = await tlRes.json();
        setTimeline(tlData);
      }

      // Weather Context
      const wRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/weather?lat=27.1767&lng=78.0081`);
      if (wRes.ok) {
        const wData = await wRes.json();
        setWeather(wData);
      }

      // Road Segments
      const rRes = await api.getRoadRisksGeoJSON();
      const mapped = (rRes.features || []).map((f: any) => ({
        id: f.properties.id,
        external_id: f.properties.external_id,
        name: f.properties.name,
        riskScore: f.properties.risk_score,
        riskLevel: f.properties.risk_level,
        isBlocked: f.properties.is_blocked,
      }));
      setRoads(mapped);
    } catch {
      // Graceful fallback
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  // Fetch explainability when selected incident changes
  useEffect(() => {
    if (selectedIncident) {
      fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/dashboard/explainability/${selectedIncident.id}`)
        .then((r) => r.json())
        .then((exp) => setExplainability(exp))
        .catch(() => setExplainability(null));
    }
  }, [selectedIncident]);

  // Live WebSocket Telemetry listener
  const handleWsEvent = (event: WsEvent) => {
    loadDashboardData();
  };

  const { isConnected } = useIncidentsSocket(handleWsEvent);

  const handleToggleRoad = async (segmentId: string, currentBlocked: boolean) => {
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/routes/segments/${segmentId}/block`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ is_blocked: !currentBlocked, reason: "Operator manual hazard closure" }),
      });
      if (res.ok) {
        loadDashboardData();
      } else {
        alert("Road blockage update requires operator privileges.");
      }
    } catch {
      alert("Error contacting API.");
    }
  };

  const handleStatusChange = async (incidentId: string, newStatus: string) => {
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/incidents/${incidentId}/status`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: newStatus }),
      });
      if (res.ok) {
        loadDashboardData();
      }
    } catch {}
  };

  return (
    <div className="max-w-7xl mx-auto py-8 px-4 space-y-6">
      {/* Top Banner & Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="font-mono text-xs px-2 py-0.5 rounded bg-critical/20 border border-critical/40 text-critical font-bold uppercase">
              OPERATOR COMMAND CENTER
            </span>
            <div className="flex items-center gap-1.5 text-xs font-mono">
              <span className={`w-2 h-2 rounded-full ${isConnected ? "bg-success animate-pulse" : "bg-muted"}`}></span>
              <span className={isConnected ? "text-success" : "text-muted"}>
                {isConnected ? "WS STREAM ACTIVE" : "WS CONNECTING"}
              </span>
            </div>
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight">Urban Flood Emergency Console</h1>
        </div>

        <button
          onClick={loadDashboardData}
          className="px-4 py-2 rounded bg-surface border border-borderDark hover:bg-surfaceHover text-xs font-mono font-semibold"
        >
          🔄 Refresh Telemetry
        </button>
      </div>

      <DisclaimerBanner />

      {/* KPI Cards Row */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        <KpiCard label="Active Incidents" value={kpis.active_incidents} variant="primary" />
        <KpiCard label="High-Risk Zones" value={kpis.high_risk_incidents} variant="critical" subtext="Risk >= 70" />
        <KpiCard label="Verified Reports" value={kpis.verified_incidents} variant="success" />
        <KpiCard label="Pending Triage" value={kpis.pending_review} variant="warning" />
        <KpiCard label="Blocked Roads" value={kpis.blocked_roads} variant="critical" />
        <KpiCard label="Simulated" value={kpis.simulated_incidents} variant="default" subtext="Demo tags" />
      </div>

      {/* Main Grid: Incident Queue & Explainability Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Incident Queue (7 cols) */}
        <div className="lg:col-span-7 p-5 rounded-lg bg-surface border border-borderDark space-y-4">
          <div className="flex items-center justify-between border-b border-borderDark pb-2">
            <h2 className="text-sm font-mono font-bold uppercase text-primary">
              Risk-Prioritized Incident Queue ({incidents.length})
            </h2>
            <span className="text-xs font-mono text-muted">Sorted by Risk Score</span>
          </div>

          <div className="space-y-2.5 max-h-[500px] overflow-y-auto pr-1">
            {incidents.map((inc) => (
              <div
                key={inc.id}
                onClick={() => setSelectedIncident(inc)}
                className={`p-3.5 rounded-lg border transition-all cursor-pointer ${
                  selectedIncident?.id === inc.id
                    ? "bg-surfaceHover border-primary"
                    : "bg-background border-borderDark hover:border-borderDark/80"
                }`}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-mono text-muted">#{inc.id.slice(0, 6)}</span>
                      <SimulatedTag isSimulated={inc.is_simulated} />
                      <FreshnessLabel minutes={inc.freshness_minutes} />
                    </div>
                    <div className="font-semibold text-sm text-foreground">{inc.title}</div>
                  </div>

                  <div className="text-right shrink-0">
                    <div className="text-xs font-mono text-muted">Risk Priority</div>
                    <div className="text-base font-bold font-mono text-critical">
                      {inc.risk_score.toFixed(1)}
                    </div>
                  </div>
                </div>

                <div className="flex flex-wrap items-center justify-between gap-2 mt-2 pt-2 border-t border-borderDark/60 text-xs font-mono">
                  <div className="flex items-center gap-2">
                    <SeverityBadge severity={inc.reported_severity} />
                    <ConfidenceBadge score={inc.confidence_score} />
                  </div>

                  <div className="flex items-center gap-1.5">
                    <select
                      value={inc.status}
                      onClick={(e) => e.stopPropagation()}
                      onChange={(e) => handleStatusChange(inc.id, e.target.value)}
                      className="bg-surface border border-borderDark rounded px-2 py-1 text-[11px] text-muted focus:border-primary"
                    >
                      <option value="reported">Reported</option>
                      <option value="under_review">Under Review</option>
                      <option value="verified">Verified</option>
                      <option value="resolved">Resolved</option>
                      <option value="rejected">Rejected</option>
                    </select>

                    <a
                      href={`/incidents/${inc.id}`}
                      onClick={(e) => e.stopPropagation()}
                      className="text-primary hover:underline text-[11px]"
                    >
                      Inspect &rarr;
                    </a>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Explainability & Road Control Panel (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          {/* Explainability Drawer */}
          <div className="p-5 rounded-lg bg-surface border border-borderDark space-y-4">
            <h2 className="text-sm font-mono font-bold uppercase text-primary border-b border-borderDark pb-2">
              Incident Explainability &amp; Avoided Roads
            </h2>

            {explainability ? (
              <div className="space-y-3 font-mono text-xs">
                <div className="font-bold text-sm text-foreground">{explainability.title}</div>

                <div className="grid grid-cols-2 gap-2 p-2.5 rounded bg-background border border-borderDark">
                  <div>
                    <span className="text-muted block text-[11px]">Priority Risk</span>
                    <span className="text-base font-bold text-critical">
                      {explainability.priority_risk_score.toFixed(1)}/100
                    </span>
                  </div>
                  <div>
                    <span className="text-muted block text-[11px]">TrustScore (Confidence)</span>
                    <span className="text-base font-bold text-primary">
                      {explainability.trust_score.toFixed(1)}/100
                    </span>
                  </div>
                </div>

                {explainability.factors && (
                  <div className="space-y-1 text-[11px] text-muted">
                    <div>• <b>Geographic:</b> {explainability.factors.geographic_reason}</div>
                    <div>• <b>Temporal:</b> {explainability.factors.temporal_reason}</div>
                    <div>• <b>Visual:</b> {explainability.factors.visual_reason}</div>
                    <div>• <b>Sources:</b> {explainability.factors.independent_sources_reason}</div>
                  </div>
                )}

                {/* Roads Avoided list */}
                <div className="border-t border-borderDark pt-2">
                  <span className="text-warning font-semibold block text-[11px] uppercase mb-1">
                    Roads Excluded from Dijkstra Routes:
                  </span>
                  {explainability.affected_roads_avoided && explainability.affected_roads_avoided.length > 0 ? (
                    <div className="space-y-1">
                      {explainability.affected_roads_avoided.map((rd: any, i: number) => (
                        <div key={i} className="flex justify-between items-center p-1.5 rounded bg-background text-[11px]">
                          <span>{rd.name}</span>
                          <span className="text-critical font-bold">Risk: {rd.risk_score}</span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-muted text-[11px]">No road closures mapped to this report yet.</div>
                  )}
                </div>
              </div>
            ) : (
              <div className="py-12 text-center text-muted font-mono text-xs">
                Select an incident from the queue to inspect AI factors and routing impact.
              </div>
            )}
          </div>

          {/* Road Blockage Manual Override Controls */}
          <div className="p-5 rounded-lg bg-surface border border-borderDark space-y-3">
            <h2 className="text-sm font-mono font-bold uppercase text-primary border-b border-borderDark pb-2">
              Operator Road Closures (Instant Reroute)
            </h2>
            <div className="space-y-2 max-h-48 overflow-y-auto">
              {roads.map((rd) => (
                <div
                  key={rd.id}
                  className="flex items-center justify-between p-2 rounded bg-background border border-borderDark text-xs font-mono"
                >
                  <div>
                    <span className="font-semibold block">{rd.name}</span>
                    <span className="text-[10px] text-muted">Risk: {rd.riskScore.toFixed(0)}/100</span>
                  </div>
                  <button
                    onClick={() => handleToggleRoad(rd.external_id || rd.id, rd.isBlocked)}
                    className={`px-2.5 py-1 rounded text-[11px] font-bold uppercase transition-all ${
                      rd.isBlocked
                        ? "bg-critical text-white hover:bg-critical/80"
                        : "bg-surface border border-borderDark text-muted hover:text-foreground"
                    }`}
                  >
                    {rd.isBlocked ? "BLOCKED (CLICK TO OPEN)" : "OPEN (CLICK TO BLOCK)"}
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Row: Realtime Weather Context & Timeline */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Weather Context Panel */}
        <div className="p-5 rounded-lg bg-surface border border-borderDark space-y-3">
          <div className="flex items-center justify-between border-b border-borderDark pb-2">
            <h3 className="font-mono text-xs uppercase text-primary font-bold">
              Meteorological Context (Open-Meteo)
            </h3>
            <span className="text-[11px] font-mono text-muted">Agra (27.18°N, 78.01°E)</span>
          </div>

          {weather && (
            <div className="space-y-3 font-mono text-xs">
              <div className="flex items-center justify-between p-3 rounded bg-background border border-borderDark">
                <div>
                  <span className="text-muted block text-[11px]">Current Rainfall</span>
                  <span className="text-xl font-bold text-foreground">
                    {weather.current_precipitation_mm} mm/hr
                  </span>
                </div>
                <div>
                  <span className="text-muted block text-[11px]">Precipitation Probability</span>
                  <span className="text-xl font-bold text-primary">
                    {weather.rain_probability_pct}%
                  </span>
                </div>
              </div>

              <div className="text-muted text-[11px]">
                Condition: <strong className="text-foreground">{weather.condition_summary}</strong>
              </div>

              {/* Weather Disclaimer Rule */}
              <div className="p-2 rounded bg-surface border border-warning/30 text-warning text-[11px]">
                ⚠️ {weather.disclaimer}
              </div>
            </div>
          )}
        </div>

        {/* Live System Timeline */}
        <div className="p-5 rounded-lg bg-surface border border-borderDark space-y-3">
          <div className="flex items-center justify-between border-b border-borderDark pb-2">
            <h3 className="font-mono text-xs uppercase text-primary font-bold">
              Live Dispatch Timeline
            </h3>
            <span className="text-[11px] font-mono text-muted">Recent updates</span>
          </div>

          <div className="space-y-2 max-h-48 overflow-y-auto">
            {timeline.map((evt, idx) => (
              <div key={idx} className="p-2 rounded bg-background border border-borderDark text-xs font-mono">
                <div className="flex items-center justify-between text-muted text-[10px]">
                  <span>{evt.event_type}</span>
                  <span>{new Date(evt.created_at).toLocaleTimeString()}</span>
                </div>
                <div className="font-bold text-foreground mt-0.5">{evt.title}</div>
                <div className="text-muted text-[11px]">{evt.description}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
