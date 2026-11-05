"use client";

import { useState } from "react";

export default function ReportPage() {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [severity, setSeverity] = useState("medium");

  return (
    <div className="max-w-2xl mx-auto py-10 px-4 space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Report Flood Incident</h1>
        <p className="text-sm text-muted">
          Ground reports are correlated with Gemini AI vision and independent signals.
        </p>
      </div>

      <div className="p-4 rounded-lg bg-surface border border-borderDark space-y-4">
        <div>
          <label className="block text-xs font-mono uppercase text-muted mb-1">Title</label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full bg-background border border-borderDark rounded px-3 py-2 text-sm focus:outline-none focus:border-primary"
            placeholder="e.g. Waterlogged intersection at MG Road"
          />
        </div>

        <div>
          <label className="block text-xs font-mono uppercase text-muted mb-1">Description</label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={3}
            className="w-full bg-background border border-borderDark rounded px-3 py-2 text-sm focus:outline-none focus:border-primary"
            placeholder="Describe visible water levels, vehicle passability, or blocked drains..."
          />
        </div>

        <div>
          <label className="block text-xs font-mono uppercase text-muted mb-1">Reported Severity</label>
          <select
            value={severity}
            onChange={(e) => setSeverity(e.target.value)}
            className="w-full bg-background border border-borderDark rounded px-3 py-2 text-sm focus:outline-none focus:border-primary"
          >
            <option value="low">Low (Passable puddle)</option>
            <option value="medium">Medium (Wheel-level water, slow traffic)</option>
            <option value="high">High (Deep water, submerged cars)</option>
            <option value="critical">Critical (Fast flowing, impassable)</option>
          </select>
        </div>

        <div>
          <label className="block text-xs font-mono uppercase text-muted mb-1">Upload Photo (Max 5MB)</label>
          <div className="border-2 border-dashed border-borderDark hover:border-primary rounded-lg p-6 text-center cursor-pointer transition-colors">
            <span className="text-sm text-muted">Click or drag &amp; drop flood photo</span>
          </div>
        </div>

        <button
          type="button"
          className="w-full py-2.5 rounded bg-primary text-background font-semibold hover:bg-primary-light text-sm transition-colors"
        >
          Submit for AI Verification
        </button>
      </div>
    </div>
  );
}
