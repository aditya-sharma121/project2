"use client";

export default function IncidentDetailPage({ params }: { params: { id: string } }) {
  return (
    <div className="max-w-4xl mx-auto py-10 px-4 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <span className="font-mono text-xs text-muted">INCIDENT #{params.id}</span>
          <h1 className="text-2xl font-bold">Flood Incident Assessment</h1>
        </div>
        <span className="px-3 py-1 rounded bg-warning/20 border border-warning/40 text-warning text-xs font-mono">
          Under Review
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="p-4 rounded-lg bg-surface border border-borderDark space-y-3">
          <h3 className="font-semibold text-sm uppercase font-mono text-primary">Gemini AI Vision</h3>
          <p className="text-sm text-muted">Analysis pending or simulated.</p>
        </div>

        <div className="p-4 rounded-lg bg-surface border border-borderDark space-y-3">
          <h3 className="font-semibold text-sm uppercase font-mono text-primary">TrustScore Breakdown</h3>
          <p className="text-sm text-muted">Spatial, temporal, visual, and independence breakdown.</p>
        </div>
      </div>
    </div>
  );
}
