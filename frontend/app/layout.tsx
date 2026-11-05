import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AFTERFLOW | AI-Powered Urban Flood Intelligence",
  description: "When roads fail, intelligence takes over. AI-powered urban flood intelligence and hazard-aware route optimization.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-background text-foreground antialiased selection:bg-primary selection:text-background">
        <header className="border-b border-borderDark bg-surface/80 backdrop-blur sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <a href="/" className="flex items-center space-x-2">
                <span className="w-3 h-3 rounded-full bg-primary animate-pulse"></span>
                <span className="font-mono font-bold tracking-wider text-xl text-primary">AFTERFLOW</span>
              </a>
              <span className="text-xs px-2 py-0.5 rounded border border-warning/30 bg-warning/10 text-warning font-mono">
                PROTOTYPE
              </span>
            </div>

            <nav className="flex items-center space-x-6 text-sm font-medium">
              <a href="/map" className="hover:text-primary transition-colors">Live Map</a>
              <a href="/report" className="hover:text-primary transition-colors">Report Flood</a>
              <a href="/routes" className="hover:text-primary transition-colors">Hazard Routing</a>
              <a href="/dashboard" className="hover:text-primary transition-colors">Operator</a>
              <a href="/about" className="text-muted hover:text-foreground transition-colors">About</a>
              <a
                href="/login"
                className="px-3 py-1.5 rounded bg-primary/10 border border-primary/30 text-primary hover:bg-primary hover:text-background font-mono text-xs transition-all"
              >
                Sign In
              </a>
            </nav>
          </div>
        </header>

        {/* Global Advisory Banner */}
        <div className="bg-warning/10 border-b border-warning/20 px-4 py-1.5 text-center text-xs text-warning font-mono">
          DECISION-SUPPORT NOTICE: AFTERFLOW is an advisory prototype and not an official emergency service. Routes are not guaranteed safe. Follow official civil defense directives.
        </div>

        <main className="min-h-[calc(100vh-100px)]">
          {children}
        </main>
      </body>
    </html>
  );
}
