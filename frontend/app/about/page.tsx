export default function AboutPage() {
  return (
    <div className="max-w-3xl mx-auto py-12 px-4 space-y-6">
      <h1 className="text-3xl font-bold">About AFTERFLOW</h1>
      <p className="text-muted leading-relaxed">
        AFTERFLOW was built for the 48-hour hackathon prototype challenge to provide real-time urban flood intelligence and hazard-aware routing.
      </p>

      <div className="p-4 rounded-lg bg-surface border border-borderDark space-y-2">
        <h3 className="font-semibold text-primary">Disclaimer &amp; Intended Use</h3>
        <p className="text-sm text-muted">
          AFTERFLOW is a prototype decision-support tool, NOT an official emergency dispatch service. Routes are never labeled &ldquo;guaranteed safe&rdquo;. Always defer to municipal authorities, emergency responders, and official evacuation notices.
        </p>
      </div>

      <div className="p-4 rounded-lg bg-surface border border-borderDark space-y-2">
        <h3 className="font-semibold text-primary">Technical Highlights</h3>
        <ul className="list-disc list-inside text-sm text-muted space-y-1">
          <li>Google Gemini Vision AI with strict prompt guardrails (no water depth hallucination).</li>
          <li>Perceptual hashing (pHash) and spatio-temporal clustering for duplicate deduplication.</li>
          <li>Multi-signal TrustScore correlation (Geographic, Temporal, Visual, Independence).</li>
          <li>NetworkX Dijkstra hazard-aware routing with road segment risk penalization.</li>
          <li>Real-time telemetry via FastAPI WebSockets and Leaflet mapping.</li>
        </ul>
      </div>
    </div>
  );
}
