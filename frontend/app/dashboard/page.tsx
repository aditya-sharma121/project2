"use client";

export default function OperatorDashboard() {
  return (
    <div className="max-w-7xl mx-auto py-8 px-4 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Operator Command Center</h1>
          <p className="text-sm text-muted">Incident triage, road blockage controls, and live telemetry</p>
        </div>
        <span className="px-3 py-1 rounded bg-critical/20 border border-critical/40 text-critical text-xs font-mono">
          OPERATOR ACCESS
        </span>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="p-4 rounded-lg bg-surface border border-borderDark">
          <div className="text-xs font-mono text-muted uppercase">Active Incidents</div>
          <div className="text-2xl font-bold mt-1 text-foreground">0</div>
        </div>
        <div className="p-4 rounded-lg bg-surface border border-borderDark">
          <div className="text-xs font-mono text-muted uppercase">High-Risk Zones</div>
          <div className="text-2xl font-bold mt-1 text-critical">0</div>
        </div>
        <div className="p-4 rounded-lg bg-surface border border-borderDark">
          <div className="text-xs font-mono text-muted uppercase">Verified Reports</div>
          <div className="text-2xl font-bold mt-1 text-success">0</div>
        </div>
        <div className="p-4 rounded-lg bg-surface border border-borderDark">
          <div className="text-xs font-mono text-muted uppercase">Pending Corroboration</div>
          <div className="text-2xl font-bold mt-1 text-warning">0</div>
        </div>
      </div>
    </div>
  );
}
