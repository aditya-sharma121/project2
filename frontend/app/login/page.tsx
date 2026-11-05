"use client";

import { useState } from "react";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<"citizen" | "operator">("citizen");

  return (
    <div className="max-w-md mx-auto py-16 px-4">
      <div className="bg-surface border border-borderDark rounded-lg p-6 space-y-6">
        <div>
          <h2 className="text-xl font-bold">Sign In to AFTERFLOW</h2>
          <p className="text-sm text-muted">Access reporting tools or operator command console.</p>
        </div>

        <form className="space-y-4" onSubmit={(e) => e.preventDefault()}>
          <div>
            <label className="block text-xs font-mono uppercase text-muted mb-1">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-background border border-borderDark rounded px-3 py-2 text-sm focus:outline-none focus:border-primary"
              placeholder="user@example.com"
            />
          </div>

          <div>
            <label className="block text-xs font-mono uppercase text-muted mb-1">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-background border border-borderDark rounded px-3 py-2 text-sm focus:outline-none focus:border-primary"
              placeholder="••••••••"
            />
          </div>

          <div>
            <label className="block text-xs font-mono uppercase text-muted mb-1">Role</label>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => setRole("citizen")}
                className={`py-2 text-xs font-mono rounded border transition-colors ${
                  role === "citizen" ? "bg-primary/20 border-primary text-primary" : "border-borderDark text-muted"
                }`}
              >
                Citizen
              </button>
              <button
                type="button"
                onClick={() => setRole("operator")}
                className={`py-2 text-xs font-mono rounded border transition-colors ${
                  role === "operator" ? "bg-primary/20 border-primary text-primary" : "border-borderDark text-muted"
                }`}
              >
                Operator
              </button>
            </div>
          </div>

          <button
            type="submit"
            className="w-full py-2.5 rounded bg-primary text-background font-semibold hover:bg-primary-light text-sm transition-colors"
          >
            Authenticate
          </button>
        </form>
      </div>
    </div>
  );
}
