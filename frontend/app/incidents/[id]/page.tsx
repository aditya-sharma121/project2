"use client";

import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { SeverityBadge } from "@/components/SeverityBadge";
import { ConfidenceBadge } from "@/components/ConfidenceBadge";
import { FreshnessLabel } from "@/components/FreshnessLabel";
import { SimulatedTag } from "@/components/SimulatedTag";
import { DisclaimerBanner } from "@/components/DisclaimerBanner";

export default function IncidentDetailPage({ params }: { params: { id: string } }) {
  const [incident, setIncident] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [updatingStatus, setUpdatingStatus] = useState(false);
  const [statusVal, setStatusVal] = useState("");

  const loadData = async () => {
    try {
      setLoading(true);
      const data = await api.getIncident(params.id);
      setIncident(data);
      setStatusVal(data.status);
    } catch (e: any) {
      setError(e.message || "Failed to load incident details");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [params.id]);

  const handleStatusChange = async (newStatus: string) => {
    try {
      setUpdatingStatus(true);
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/incidents/${params.id}/status`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: newStatus, note: "Operator manual status update" }),
      });
      if (res.ok) {
        await loadData();
      } else {
        alert("Status update requires operator privileges or valid status.");
      }
    } catch {
      alert("Network error updating status.");
    } finally {
      setUpdatingStatus(false);
    }
  };

  const handleReverify = async () => {
    try {
      await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/incidents/${params.id}/verify`, {
        method: "POST"
      });
      await loadData();
    } catch {
      alert("Verification update failed.");
    }
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto py-16 text-center font-mono text-muted">
        Loading incident telemetry &amp; verification signals...
      </div>
    );
  }

  if (error || !incident) {
    return (
      <div className="max-w-4xl mx-auto py-16 text-center font-mono text-critical">
        {error || "Incident not found"}
      </div>
    );
  }

  const verif = incident.latest_verification;
  const factors = verif?.explanation || {};

  return (
    <div className="max-w-5xl mx-auto py-8 px-4 space-y-6">
      <DisclaimerBanner />

      {/* Header Panel */}
      <div className="p-6 rounded-lg bg-surface border border-borderDark flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="font-mono text-xs text-muted">INCIDENT #{incident.id.slice(0, 8)}</span>
            <SimulatedTag isSimulated={incident.is_simulated} />
            <FreshnessLabel minutes={incident.freshness_minutes} />
          </div>
          <h1 className="text-2xl font-bold">{incident.title}</h1>
          <p className="text-sm text-muted mt-1">{incident.description || "No narrative details provided."}</p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <SeverityBadge severity={incident.reported_severity} />
          <ConfidenceBadge score={incident.confidence_score} label={verif?.confidence_label} />
          <div className="px-3 py-1 rounded bg-background border border-borderDark text-xs font-mono">
            Priority Risk: <strong className="text-critical">{incident.risk_score.toFixed(1)}/100</strong>
          </div>
        </div>
      </div>

      {/* Core Grid: AI Vision & TrustScore Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Left: Ground Evidence & Gemini AI Analysis */}
        <div className="p-5 rounded-lg bg-surface border border-borderDark space-y-4">
          <div className="flex items-center justify-between border-b border-borderDark pb-2">
            <h3 className="font-mono text-xs uppercase text-primary font-bold">
              Ground Evidence &amp; AI Vision
            </h3>
            <span className="text-xs text-muted font-mono">
              {incident.evidence?.length || 0} photo(s)
            </span>
          </div>

          {incident.evidence && incident.evidence.length > 0 ? (
            incident.evidence.map((ev: any, idx: number) => {
              const ai = ev.ai_result || {};
              return (
                <div key={idx} className="space-y-3 p-3 rounded bg-background border border-borderDark">
                  <div className="relative">
                    <img
                      src={ev.image_url}
                      alt="Ground Evidence"
                      className="w-full h-48 object-cover rounded border border-borderDark"
                    />
                    {ev.is_duplicate && (
                      <span className="absolute top-2 right-2 px-2 py-0.5 rounded bg-critical text-white text-[10px] font-mono font-bold">
                        DUPLICATE IMAGE
                      </span>
                    )}
                  </div>

                  {/* AI Output Breakdown */}
                  <div className="grid grid-cols-2 gap-2 text-xs font-mono">
                    <div>
                      <span className="text-muted block">Classification</span>
                      <span className="text-foreground font-semibold">{ai.classification || "N/A"}</span>
                    </div>
                    <div>
                      <span className="text-muted block">Visible Water</span>
                      <span className={`font-semibold ${ai.visible_water ? "text-critical" : "text-success"}`}>
                        {ai.visible_water ? "Yes" : "None"}
                      </span>
                    </div>
                    <div>
                      <span className="text-muted block">Estimated Coverage</span>
                      <span className="text-foreground">{((ai.estimated_coverage || 0) * 100).toFixed(0)}%</span>
                    </div>
                    <div>
                      <span className="text-muted block">AI Confidence</span>
                      <span className="text-primary">{((ai.confidence || 0) * 100).toFixed(0)}%</span>
                    </div>
                  </div>

                  {ai.limitations && (
                    <div className="text-[11px] font-mono text-muted bg-surface p-2 rounded space-y-1">
                      <span className="text-warning font-semibold block">⚠️ AI Limitations:</span>
                      {ai.limitations.map((l: string, i: number) => (
                        <div key={i}>• {l}</div>
                      ))}
                    </div>
                  )}
                </div>
              );
            })
          ) : (
            <div className="py-12 text-center text-muted font-mono text-xs">
              No ground evidence photos submitted for this report yet.
            </div>
          )}
        </div>

        {/* Right: Multi-Factor TrustScore Breakdown */}
        <div className="p-5 rounded-lg bg-surface border border-borderDark space-y-4">
          <div className="flex items-center justify-between border-b border-borderDark pb-2">
            <h3 className="font-mono text-xs uppercase text-primary font-bold">
              Multi-Factor TrustScore Engine
            </h3>
            <button
              onClick={handleReverify}
              className="text-xs font-mono text-primary hover:underline"
            >
              🔄 Recalculate
            </button>
          </div>

          <div className="p-4 rounded bg-background border border-borderDark text-center space-y-1">
            <div className="text-xs font-mono text-muted uppercase">Corroborated TrustScore</div>
            <div className="text-4xl font-extrabold text-foreground font-mono">
              {incident.confidence_score.toFixed(1)} <span className="text-sm text-muted">/ 100</span>
            </div>
            <div className="pt-1">
              <ConfidenceBadge score={incident.confidence_score} label={verif?.confidence_label} />
            </div>
          </div>

          {/* Component Factors Bars */}
          <div className="space-y-3 font-mono text-xs">
            {/* G Factor */}
            <div>
              <div className="flex justify-between text-muted mb-1">
                <span>[G] Geographic Agreement (25%)</span>
                <span>{verif?.geographic_agreement?.toFixed(1) || 0}/100</span>
              </div>
              <div className="w-full h-2 rounded bg-background overflow-hidden border border-borderDark">
                <div
                  className="h-full bg-primary"
                  style={{ width: `${verif?.geographic_agreement || 0}%` }}
                ></div>
              </div>
              <p className="text-[11px] text-muted mt-1">{factors.geographic_reason}</p>
            </div>

            {/* Tm Factor */}
            <div>
              <div className="flex justify-between text-muted mb-1">
                <span>[Tm] Temporal Agreement (20%)</span>
                <span>{verif?.temporal_agreement?.toFixed(1) || 0}/100</span>
              </div>
              <div className="w-full h-2 rounded bg-background overflow-hidden border border-borderDark">
                <div
                  className="h-full bg-warning"
                  style={{ width: `${verif?.temporal_agreement || 0}%` }}
                ></div>
              </div>
              <p className="text-[11px] text-muted mt-1">{factors.temporal_reason}</p>
            </div>

            {/* V Factor */}
            <div>
              <div className="flex justify-between text-muted mb-1">
                <span>[V] Visual Quality (35%)</span>
                <span>{verif?.visual_quality?.toFixed(1) || 0}/100</span>
              </div>
              <div className="w-full h-2 rounded bg-background overflow-hidden border border-borderDark">
                <div
                  className="h-full bg-success"
                  style={{ width: `${verif?.visual_quality || 0}%` }}
                ></div>
              </div>
              <p className="text-[11px] text-muted mt-1">{factors.visual_reason}</p>
            </div>

            {/* I Factor */}
            <div>
              <div className="flex justify-between text-muted mb-1">
                <span>[I] Independent Sources (20%)</span>
                <span>{verif?.independent_source_quality?.toFixed(1) || 0}/100</span>
              </div>
              <div className="w-full h-2 rounded bg-background overflow-hidden border border-borderDark">
                <div
                  className="h-full bg-purple-400"
                  style={{ width: `${verif?.independent_source_quality || 0}%` }}
                ></div>
              </div>
              <p className="text-[11px] text-muted mt-1">{factors.independent_sources_reason}</p>
            </div>
          </div>

          <div className="text-[10px] font-mono text-muted border-t border-borderDark pt-2">
            Formula: TrustScore = 0.25G + 0.20Tm + 0.35V + 0.20I (Heuristic weights)
          </div>
        </div>
      </div>

      {/* Operator Control Panel */}
      <div className="p-5 rounded-lg bg-surface border border-borderDark space-y-3">
        <h3 className="font-mono text-xs uppercase text-primary font-bold">
          Operator Triage &amp; Status Controls
        </h3>
        <div className="flex flex-wrap items-center gap-2">
          {["reported", "under_review", "verified", "resolved", "rejected"].map((st) => (
            <button
              key={st}
              disabled={updatingStatus}
              onClick={() => handleStatusChange(st)}
              className={`px-3 py-1.5 rounded text-xs font-mono uppercase tracking-wider border transition-all ${
                incident.status === st
                  ? "bg-primary text-background border-primary font-bold"
                  : "border-borderDark text-muted hover:text-foreground"
              }`}
            >
              Mark {st.replace("_", " ")}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
