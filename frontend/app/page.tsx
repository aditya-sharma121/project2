export default function HomePage() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-12">
      {/* Hero Section */}
      <div className="text-center py-16 space-y-6">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-primary/30 bg-primary/10 text-primary text-xs font-mono uppercase tracking-widest">
          Urban Flood Intelligence &amp; Route Optimization
        </div>
        <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight">
          When roads fail, <span className="text-primary">intelligence takes over.</span>
        </h1>
        <p className="max-w-2xl mx-auto text-muted text-lg">
          Correlating citizen ground evidence with Gemini AI computer vision, calculating uncertainty-aware TrustScores, and generating dynamic hazard-avoiding routes in real-time.
        </p>

        <div className="flex flex-wrap justify-center gap-4 pt-4">
          <a
            href="/report"
            className="px-6 py-3 rounded-md bg-primary text-background font-semibold hover:bg-primary-light transition-colors"
          >
            Report Flood Incident
          </a>
          <a
            href="/map"
            className="px-6 py-3 rounded-md bg-surface border border-borderDark text-foreground hover:bg-surfaceHover transition-colors"
          >
            Explore Live Hazard Map
          </a>
          <a
            href="/routes"
            className="px-6 py-3 rounded-md bg-surface border border-borderDark text-foreground hover:bg-surfaceHover transition-colors"
          >
            Calculate Safe Route
          </a>
        </div>
      </div>

      {/* 4-Step Architecture Pipeline */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 py-12">
        <div className="p-6 rounded-lg bg-surface border border-borderDark space-y-3">
          <div className="font-mono text-primary text-sm">01 / VISION</div>
          <h3 className="font-bold text-lg">Image Assessment</h3>
          <p className="text-sm text-muted">
            Gemini vision extracts visible water bounds and coverage without hallucinating exact water depth.
          </p>
        </div>

        <div className="p-6 rounded-lg bg-surface border border-borderDark space-y-3">
          <div className="font-mono text-primary text-sm">02 / CORRELATION</div>
          <h3 className="font-bold text-lg">Independent Reports</h3>
          <p className="text-sm text-muted">
            Perceptual hashing (pHash) and spatial-temporal clustering eliminate duplicate and bot submissions.
          </p>
        </div>

        <div className="p-6 rounded-lg bg-surface border border-borderDark space-y-3">
          <div className="font-mono text-primary text-sm">03 / TRUSTSCORE</div>
          <h3 className="font-bold text-lg">Uncertainty Risk</h3>
          <p className="text-sm text-muted">
            Heuristic fusion of spatial (G), temporal (Tm), visual (V), and independent source (I) signals.
          </p>
        </div>

        <div className="p-6 rounded-lg bg-surface border border-borderDark space-y-3">
          <div className="font-mono text-primary text-sm">04 / ROUTING</div>
          <h3 className="font-bold text-lg">Hazard Routing</h3>
          <p className="text-sm text-muted">
            NetworkX Dijkstra graph engine routes vehicles around submerged or high-risk segments dynamically.
          </p>
        </div>
      </div>
    </div>
  );
}
