"use client";

export default function MapPage() {
  return (
    <div className="h-[calc(100vh-130px)] flex flex-col sm:flex-row">
      <div className="w-full sm:w-80 p-4 border-r border-borderDark bg-surface flex flex-col space-y-4">
        <h2 className="text-lg font-bold">Flood Layers</h2>
        <div className="space-y-2 text-sm">
          <label className="flex items-center space-x-2">
            <input type="checkbox" defaultChecked className="rounded bg-background border-borderDark text-primary" />
            <span>Active Incidents</span>
          </label>
          <label className="flex items-center space-x-2">
            <input type="checkbox" defaultChecked className="rounded bg-background border-borderDark text-primary" />
            <span>Road Segment Risk Lines</span>
          </label>
          <label className="flex items-center space-x-2">
            <input type="checkbox" defaultChecked className="rounded bg-background border-borderDark text-primary" />
            <span>Critical Facilities</span>
          </label>
        </div>
      </div>
      <div className="flex-1 bg-background relative flex items-center justify-center">
        <p className="text-muted font-mono text-sm">Leaflet OpenStreetMap Map Viewport (Interactive map in Phase 11)</p>
      </div>
    </div>
  );
}
