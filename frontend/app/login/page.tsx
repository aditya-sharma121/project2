"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { api, ApiException } from "@/lib/api";
import { DisclaimerBanner } from "@/components/DisclaimerBanner";

export default function LoginPage() {
  const router = useRouter();
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [role, setRole] = useState<"citizen" | "operator">("citizen");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      if (isRegister) {
        // Register
        const res = await fetch(`${apiUrl}/api/v1/auth/register`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password, full_name: fullName, role }),
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error?.message || "Registration failed");

        // Auto login
        const loginRes = await fetch(`${apiUrl}/api/v1/auth/login`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password }),
        });
        const loginData = await loginRes.json();
        if (loginData.access_token) {
          api.setToken(loginData.access_token);
          router.push(role === "operator" ? "/dashboard" : "/map");
        }
      } else {
        // Login
        const loginRes = await fetch(`${apiUrl}/api/v1/auth/login`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password }),
        });
        const loginData = await loginRes.json();
        if (!loginRes.ok) throw new Error(loginData.error?.message || "Invalid email or password");

        if (loginData.access_token) {
          api.setToken(loginData.access_token);
          router.push(loginData.user?.role === "operator" ? "/dashboard" : "/map");
        }
      }
    } catch (err: any) {
      setError(err.message || "Authentication failed");
    } finally {
      setLoading(false);
    }
  };

  const handleDemoLogin = async (demoRole: "operator" | "citizen") => {
    setEmail(demoRole === "operator" ? "operator@afterflow.gov" : "citizen1@agra.org");
    setPassword(demoRole === "operator" ? "operatorpassword" : "citizenpassword");
    setRole(demoRole);
  };

  return (
    <div className="max-w-md mx-auto py-12 px-4 space-y-6">
      <DisclaimerBanner />

      <div className="bg-surface border border-borderDark rounded-lg p-6 space-y-5">
        <div>
          <h2 className="text-xl font-bold">
            {isRegister ? "Create AFTERFLOW Account" : "Sign In to AFTERFLOW"}
          </h2>
          <p className="text-xs text-muted font-mono mt-1">
            Role-based access for citizens and emergency response operators.
          </p>
        </div>

        {error && (
          <div className="p-3 rounded bg-critical/10 border border-critical/30 text-critical text-xs font-mono">
            {error}
          </div>
        )}

        {/* Quick Demo Pre-fill Buttons */}
        <div className="p-3 rounded bg-background border border-borderDark space-y-1.5 text-xs font-mono">
          <span className="text-muted block text-[11px] uppercase">Quick Demo Credentials:</span>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => handleDemoLogin("operator")}
              className="flex-1 py-1 rounded bg-critical/20 border border-critical/40 text-critical font-bold text-[11px]"
            >
              Major Sharma (Operator)
            </button>
            <button
              type="button"
              onClick={() => handleDemoLogin("citizen")}
              className="flex-1 py-1 rounded bg-primary/20 border border-primary/40 text-primary font-bold text-[11px]"
            >
              Aarav Mehta (Citizen)
            </button>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4 text-xs font-mono">
          {isRegister && (
            <div>
              <label className="block uppercase text-muted mb-1 font-semibold">Full Name</label>
              <input
                type="text"
                required
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="Major R. Sharma"
                className="w-full bg-background border border-borderDark rounded px-3 py-2 text-sm focus:border-primary focus:outline-none"
              />
            </div>
          )}

          <div>
            <label className="block uppercase text-muted mb-1 font-semibold">Email Address</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="user@afterflow.gov"
              className="w-full bg-background border border-borderDark rounded px-3 py-2 text-sm focus:border-primary focus:outline-none"
            />
          </div>

          <div>
            <label className="block uppercase text-muted mb-1 font-semibold">Password</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full bg-background border border-borderDark rounded px-3 py-2 text-sm focus:border-primary focus:outline-none"
            />
          </div>

          {isRegister && (
            <div>
              <label className="block uppercase text-muted mb-1 font-semibold">Account Role</label>
              <div className="grid grid-cols-2 gap-2">
                <button
                  type="button"
                  onClick={() => setRole("citizen")}
                  className={`py-2 text-xs font-mono rounded border uppercase transition-colors ${
                    role === "citizen" ? "bg-primary/20 border-primary text-primary font-bold" : "border-borderDark text-muted"
                  }`}
                >
                  Citizen Reporter
                </button>
                <button
                  type="button"
                  onClick={() => setRole("operator")}
                  className={`py-2 text-xs font-mono rounded border uppercase transition-colors ${
                    role === "operator" ? "bg-critical/20 border-critical text-critical font-bold" : "border-borderDark text-muted"
                  }`}
                >
                  Emergency Operator
                </button>
              </div>
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 rounded bg-primary text-background font-bold text-sm uppercase tracking-wider hover:bg-primary-light transition-all mt-2"
          >
            {loading ? "Authenticating..." : isRegister ? "Create Account" : "Authenticate"}
          </button>
        </form>

        <div className="text-center pt-2 text-xs font-mono text-muted">
          <button
            type="button"
            onClick={() => setIsRegister(!isRegister)}
            className="text-primary hover:underline"
          >
            {isRegister ? "Already registered? Sign In &rarr;" : "Need an account? Register here &rarr;"}
          </button>
        </div>
      </div>
    </div>
  );
}
