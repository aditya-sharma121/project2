"use client";

import { useState } from "react";

export default function RoutesPage() {
  const [avoidRisk, setAvoidRisk] = useState(true);

  return (
    <div className="max-w-4xl mx-auto py-8 px-4 space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Hazard-Aware Routing</h1>
        <p className="text-sm text-muted">
          Dynamic route optimization avoiding flooded or high-risk segments using NetworkX Dijkstra.
        </p>
      </div>

      <div className="p-4 rounded-lg bg-surface border border-borderDark space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-mono uppercase text-muted mb-1">Origin Coordinates</label>
            <input
              type="text"
              readOnly
              value="27.1767, 78.0081 (Agra Center)"
              className="w-full bg-background border border-borderDark rounded px-3 py-2 text-sm text-muted"
            />
          </div>
          <div>
            <label className="block text-xs font-mono uppercase text-muted mb-1">Destination Coordinates</label>
            <input
              type="text"
              readOnly
              value="27.1890, 78.0200 (North Hospital)"
              className="w-full bg-background border border-borderDark rounded px-3 py-2 text-sm text-muted"
            />
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <input
            type="checkbox"
            id="avoid"
            checked={avoidRisk}
            onChange={(e) => setAvoidRisk(e.target.checked)}
            className="rounded bg-background border-borderDark text-primary"
          />
          <label htmlFor="avoid" className="text-sm font-medium">
            Avoid high-risk roads (Risk score ≥ 80 or blocked)
          </label>
        </div>

        <button
          type="button"
          className="px-6 py-2.5 rounded bg-primary text-background font-semibold hover:bg-primary-light text-sm transition-colors"
        >
          Compute Routes
        </button>
      </div>
    </div>
  );
}
