/**
 * AFTERFLOW Typed API Client
 * Interfaces with FastAPI Backend at /api/v1
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface ApiError {
  code: string;
  message: string;
  details?: unknown;
}

export class ApiException extends Error {
  code: string;
  details?: unknown;

  constructor(error: ApiError, public status: number) {
    super(error.message);
    this.name = "ApiException";
    this.code = error.code;
    this.details = error.details;
  }
}

export interface User {
  id: string;
  email: string;
  role: "citizen" | "operator";
}

export interface Incident {
  id: string;
  title: string;
  description: string;
  incident_type: string;
  reported_severity: "low" | "medium" | "high" | "critical";
  ai_severity?: "none" | "low" | "medium" | "high";
  status: "reported" | "under_review" | "verified" | "resolved" | "rejected";
  confidence_score: number;
  is_simulated: boolean;
  latitude: number;
  longitude: number;
  evidence?: any[];
  latest_verification?: any;
  freshness_minutes?: number;
  created_at: string;
  updated_at: string;
}

export interface RouteResponse {
  standard_route: unknown;
  risk_aware_route: unknown;
  avoided_segments: Array<{ id: string; reason: string }>;
  disclaimer: string;
  computed_at: string;
}

class ApiClient {
  private token: string | null = null;

  setToken(token: string | null) {
    this.token = token;
    if (typeof window !== "undefined") {
      if (token) localStorage.setItem("afterflow_token", token);
      else localStorage.removeItem("afterflow_token");
    }
  }

  getToken(): string | null {
    if (this.token) return this.token;
    if (typeof window !== "undefined") {
      this.token = localStorage.getItem("afterflow_token");
    }
    return this.token;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${API_BASE}${endpoint}`;
    const headers = new Headers(options.headers || {});

    if (!headers.has("Content-Type") && !(options.body instanceof FormData)) {
      headers.set("Content-Type", "application/json");
    }

    const token = this.getToken();
    if (token) {
      headers.set("Authorization", `Bearer ${token}`);
    }

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      let errorData: ApiError = {
        code: `HTTP_${response.status}`,
        message: response.statusText || "Request failed",
      };
      try {
        const json = await response.json();
        if (json.error) {
          errorData = json.error;
        }
      } catch {
        // Fallback to default error
      }
      throw new ApiException(errorData, response.status);
    }

    return response.json();
  }

  // System
  async getHealth() {
    return this.request<{ status: string; mock_ai: boolean; disclaimer: string }>("/health");
  }

  // Auth
  async getMe(): Promise<User> {
    return this.request<User>("/api/v1/auth/me");
  }

  // Incidents
  async getIncidents(params: Record<string, string | number | boolean> = {}) {
    const query = new URLSearchParams(params as Record<string, string>).toString();
    return this.request<{ items: Incident[]; total: number }>(`/api/v1/incidents${query ? `?${query}` : ""}`);
  }

  async getIncident(id: string) {
    return this.request<Incident>(`/api/v1/incidents/${id}`);
  }

  async createIncident(formData: FormData) {
    return this.request<Incident>("/api/v1/incidents", {
      method: "POST",
      body: formData,
    });
  }

  // GeoJSON
  async getIncidentsGeoJSON() {
    return this.request<GeoJSON.FeatureCollection>("/api/v1/geo/incidents");
  }

  async getRoadRisksGeoJSON() {
    return this.request<GeoJSON.FeatureCollection>("/api/v1/geo/road-risks");
  }

  // Routes
  async calculateRoute(origin: { lat: number; lng: number }, destination: { lat: number; lng: number }, avoidHighRisk: boolean = true) {
    return this.request<RouteResponse>("/api/v1/routes/calculate", {
      method: "POST",
      body: JSON.stringify({ origin, destination, avoid_high_risk: avoidHighRisk }),
    });
  }

  // Dashboard
  async getDashboardKpis() {
    return this.request<{
      active_incidents: number;
      high_risk_incidents: number;
      verified_incidents: number;
      pending_review: number;
    }>("/api/v1/dashboard/kpis");
  }
}

export const api = new ApiClient();
