"use client";

import React, { useState } from "react";
import { api, ApiException } from "@/lib/api";
import { SeverityBadge } from "@/components/SeverityBadge";
import { ConfidenceBadge } from "@/components/ConfidenceBadge";
import { DisclaimerBanner } from "@/components/DisclaimerBanner";

export default function ReportPage() {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [severity, setSeverity] = useState("medium");
  const [lat, setLat] = useState("27.1767");
  const [lng, setLng] = useState("78.0081");
  const [isSimulated, setIsSimulated] = useState(false);

  // File states
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);

  // Submission & AI progress states
  const [submitting, setSubmitting] = useState(false);
  const [submitStep, setSubmitStep] = useState<string>("");
  const [submittedIncident, setSubmittedIncident] = useState<any | null>(null);
  const [aiResult, setAiResult] = useState<any | null>(null);

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setUploadError(null);
    if (!e.target.files || e.target.files.length === 0) {
      setImageFile(null);
      setImagePreview(null);
      return;
    }

    const file = e.target.files[0];

    // Client-side validation: format check
    const allowed = ["image/jpeg", "image/png", "image/webp"];
    if (!allowed.includes(file.type)) {
      setUploadError("Invalid image type. Please select JPEG, PNG, or WEBP.");
      return;
    }

    // Client-side validation: max 5MB
    if (file.size > 5 * 1024 * 1024) {
      setUploadError("File size exceeds 5MB limit. Please choose a smaller photo.");
      return;
    }

    setImageFile(file);
    const reader = new FileReader();
    reader.onload = (ev) => {
      setImagePreview(ev.target?.result as string);
    };
    reader.readAsDataURL(file);
  };

  const handleUseMyLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          setLat(pos.coords.latitude.toFixed(4));
          setLng(pos.coords.longitude.toFixed(4));
        },
        () => {
          // Default fallback
          setLat("27.1767");
          setLng("78.0081");
        }
      );
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title) {
      alert("Please provide a brief title for this incident.");
      return;
    }

    setSubmitting(true);
    setUploadError(null);
    setSubmitStep("Uploading evidence photo & validating metadata...");

    try {
      const formData = new FormData();
      formData.append("title", title);
      formData.append("description", description);
      formData.append("latitude", lat);
      formData.append("longitude", lng);
      formData.append("reported_severity", severity);
      formData.append("incident_type", "urban_flooding");
      formData.append("is_simulated", String(isSimulated));

      if (imageFile) {
        formData.append("image", imageFile);
      }

      setSubmitStep("Gemini Vision AI analyzing visible water coverage & bounds...");
      const result = await api.createIncident(formData);

      setSubmitStep("Correlating with independent nearby reports & calculating TrustScore...");
      
      // Fetch full incident detail including evidence & verification
      const fullDetail = await api.getIncident(result.id);
      setSubmittedIncident(fullDetail);

      if (fullDetail.evidence && fullDetail.evidence.length > 0) {
        setAiResult(fullDetail.evidence[0].ai_result);
      }
    } catch (err: any) {
      if (err instanceof ApiException) {
        setUploadError(`Submission error: ${err.message}`);
      } else {
        setUploadError("Failed to connect to backend server. Is the API running on port 8000?");
      }
    } finally {
      setSubmitting(false);
      setSubmitStep("");
    }
  };

  return (
    <div className="max-w-3xl mx-auto py-8 px-4 space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Citizen Ground Report</h1>
        <p className="text-sm text-muted">
          Report flooded streets or waterlogged junctions to trigger Gemini AI assessment and hazard routing.
        </p>
      </div>

      <DisclaimerBanner />

      {/* Success View */}
      {submittedIncident && (
        <div className="p-6 rounded-lg bg-surface border border-success/40 space-y-4">
          <div className="flex items-center justify-between">
            <span className="font-mono text-xs text-success flex items-center gap-1.5 font-bold uppercase">
              <span className="w-2 h-2 rounded-full bg-success animate-ping"></span>
              Report Verified &amp; Logged #{submittedIncident.id.slice(0, 8)}
            </span>
            <div className="flex items-center gap-2">
              <SeverityBadge severity={submittedIncident.reported_severity} />
              <ConfidenceBadge score={submittedIncident.confidence_score} />
            </div>
          </div>

          <h2 className="text-xl font-bold">{submittedIncident.title}</h2>
          <p className="text-sm text-muted">{submittedIncident.description}</p>

          {/* AI Assessment Card */}
          {aiResult && (
            <div className="mt-4 p-4 rounded bg-background/80 border border-primary/30 space-y-3">
              <div className="flex items-center justify-between border-b border-borderDark pb-2">
                <span className="text-xs font-mono text-primary font-bold">
                  GOOGLE GEMINI VISION ASSESSMENT
                </span>
                <span className="text-xs font-mono text-muted">
                  Confidence: {(aiResult.confidence * 100).toFixed(0)}%
                </span>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs font-mono">
                <div>
                  <span className="text-muted block">Classification</span>
                  <span className="font-semibold text-foreground">{aiResult.classification}</span>
                </div>
                <div>
                  <span className="text-muted block">Visible Water</span>
                  <span className={`font-semibold ${aiResult.visible_water ? "text-critical" : "text-success"}`}>
                    {aiResult.visible_water ? "Detected" : "None"}
                  </span>
                </div>
                <div>
                  <span className="text-muted block">Severity</span>
                  <span className="font-semibold text-warning">{aiResult.severity}</span>
                </div>
                <div>
                  <span className="text-muted block">Road Coverage</span>
                  <span className="font-semibold text-foreground">{(aiResult.estimated_coverage * 100).toFixed(0)}%</span>
                </div>
              </div>

              {/* Guardrail Limitations */}
              {aiResult.limitations && (
                <div className="text-[11px] font-mono text-muted/90 bg-surface p-2.5 rounded border border-borderDark space-y-1">
                  <span className="text-warning font-semibold block">⚠️ Technical Limitations (Guardrails):</span>
                  {aiResult.limitations.map((lim: string, idx: number) => (
                    <div key={idx}>• {lim}</div>
                  ))}
                </div>
              )}
            </div>
          )}

          <div className="pt-2 flex gap-3">
            <a
              href={`/incidents/${submittedIncident.id}`}
              className="px-4 py-2 rounded bg-primary text-background font-semibold text-xs font-mono hover:bg-primary-light"
            >
              View Full Incident &amp; Score Breakdown
            </a>
            <button
              type="button"
              onClick={() => {
                setSubmittedIncident(null);
                setAiResult(null);
                setTitle("");
                setDescription("");
                setImageFile(null);
                setImagePreview(null);
              }}
              className="px-4 py-2 rounded border border-borderDark text-muted hover:text-foreground text-xs font-mono"
            >
              Submit Another Report
            </button>
          </div>
        </div>
      )}

      {/* Report Form */}
      {!submittedIncident && (
        <form onSubmit={handleSubmit} className="p-6 rounded-lg bg-surface border border-borderDark space-y-5">
          {uploadError && (
            <div className="p-3 rounded bg-critical/10 border border-critical/30 text-critical text-xs font-mono">
              {uploadError}
            </div>
          )}

          <div>
            <label className="block text-xs font-mono uppercase text-muted mb-1 font-semibold">
              Location Name / Incident Title *
            </label>
            <input
              type="text"
              required
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. Submerged underpass at MG Road crossing"
              className="w-full bg-background border border-borderDark rounded px-3 py-2 text-sm focus:outline-none focus:border-primary"
            />
          </div>

          <div>
            <label className="block text-xs font-mono uppercase text-muted mb-1 font-semibold">
              Description &amp; Observed Ground Conditions
            </label>
            <textarea
              rows={3}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Describe road passability, vehicle tyre submersion, current flow, or blocked drainage..."
              className="w-full bg-background border border-borderDark rounded px-3 py-2 text-sm focus:outline-none focus:border-primary"
            />
          </div>

          {/* Location & Severity Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-mono uppercase text-muted mb-1 font-semibold">
                Reported Severity
              </label>
              <select
                value={severity}
                onChange={(e) => setSeverity(e.target.value)}
                className="w-full bg-background border border-borderDark rounded px-3 py-2 text-sm focus:outline-none focus:border-primary"
              >
                <option value="low">Low (Passable puddle)</option>
                <option value="medium">Medium (Wheel-level, slow traffic)</option>
                <option value="high">High (Submerged cars, impassable)</option>
                <option value="critical">Critical (Rapid flow / hazard)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-mono uppercase text-muted mb-1 font-semibold">
                Latitude
              </label>
              <input
                type="number"
                step="0.0001"
                value={lat}
                onChange={(e) => setLat(e.target.value)}
                className="w-full bg-background border border-borderDark rounded px-3 py-2 text-sm focus:outline-none focus:border-primary"
              />
            </div>

            <div>
              <label className="block text-xs font-mono uppercase text-muted mb-1 font-semibold">
                Longitude
              </label>
              <input
                type="number"
                step="0.0001"
                value={lng}
                onChange={(e) => setLng(e.target.value)}
                className="w-full bg-background border border-borderDark rounded px-3 py-2 text-sm focus:outline-none focus:border-primary"
              />
            </div>
          </div>

          <div className="flex items-center justify-between text-xs">
            <button
              type="button"
              onClick={handleUseMyLocation}
              className="text-primary hover:underline font-mono"
            >
              📍 Use My Current GPS Location
            </button>
            <label className="flex items-center gap-2 cursor-pointer font-mono text-muted">
              <input
                type="checkbox"
                checked={isSimulated}
                onChange={(e) => setIsSimulated(e.target.checked)}
                className="rounded bg-background border-borderDark text-primary"
              />
              <span>Mark as Simulated Test</span>
            </label>
          </div>

          {/* Photo Upload Zone */}
          <div>
            <label className="block text-xs font-mono uppercase text-muted mb-1 font-semibold">
              Ground Evidence Photo (JPEG, PNG, WEBP &le; 5MB)
            </label>
            <div className="border-2 border-dashed border-borderDark hover:border-primary/50 rounded-lg p-6 text-center cursor-pointer transition-colors relative">
              <input
                type="file"
                accept="image/jpeg,image/png,image/webp"
                onChange={handleImageChange}
                className="absolute inset-0 opacity-0 cursor-pointer w-full h-full"
              />
              {imagePreview ? (
                <div className="space-y-2">
                  <img
                    src={imagePreview}
                    alt="Flood Preview"
                    className="max-h-48 mx-auto rounded object-cover border border-borderDark"
                  />
                  <span className="text-xs font-mono text-primary block">
                    {imageFile?.name} ({(imageFile?.size! / 1024).toFixed(0)} KB) — Click to replace
                  </span>
                </div>
              ) : (
                <div className="space-y-1">
                  <div className="text-3xl">📷</div>
                  <div className="text-sm font-medium text-foreground">Click or drag &amp; drop flood photo</div>
                  <div className="text-xs text-muted font-mono">Strictly analyzed for visible flood evidence by Gemini AI</div>
                </div>
              )}
            </div>
          </div>

          {/* Submission Button with Progress feedback */}
          <div>
            <button
              type="submit"
              disabled={submitting}
              className={`w-full py-3 rounded font-semibold text-sm transition-all font-mono uppercase tracking-wider ${
                submitting
                  ? "bg-primary/50 text-background cursor-not-allowed"
                  : "bg-primary text-background hover:bg-primary-light"
              }`}
            >
              {submitting ? "Processing Evidence..." : "Submit Incident for AI Verification"}
            </button>
            {submitting && (
              <p className="text-xs text-primary font-mono text-center mt-2 animate-pulse">
                {submitStep}
              </p>
            )}
          </div>
        </form>
      )}
    </div>
  );
}
