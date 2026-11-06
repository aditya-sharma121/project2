# AFTERFLOW API Contract Changelog

All schemas conform to base path `/api/v1` and return standard JSON error payload:
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable description",
    "details": null
  }
}
```

---

## [Phase 14] - Complete Monolith & 48-Hour Hackathon Prototype

### Endpoints
- **System**:
  - `GET /health`: Health status, disclaimer, mock_ai flag.
  - `WS /ws/incidents`: Real-time incident & routing telemetry WebSocket stream. Events:
    - `incident.created`
    - `incident.updated`
    - `incident.status_changed`
    - `route.hazard_updated`
- **Auth**:
  - `POST /api/v1/auth/register`: Register citizen or operator.
  - `POST /api/v1/auth/login`: Authenticate and issue JWT.
  - `GET /api/v1/auth/me`: Current authenticated user profile.
- **Incidents**:
  - `POST /api/v1/incidents`: Multipart form upload (title, description, lat, lng, severity, optional photo). Automatically triggers pHash deduplication, Gemini vision assessment, TrustScore calculation, and priority risk mapping.
  - `GET /api/v1/incidents`: Filtered incident list with pagination, freshness calculations, and staleness badges.
  - `GET /api/v1/incidents/{id}`: Detailed incident view with evidence list and latest verification.
  - `PATCH /api/v1/incidents/{id}/status`: Operator status control (reported, under_review, verified, resolved, rejected).
  - `POST /api/v1/incidents/{id}/verify`: On-demand re-verification and TrustScore calculation.
  - `GET /api/v1/incidents/{id}/trust-score`: Multi-factor TrustScore breakdown.
- **Evidence**:
  - `GET /api/v1/evidence`: List evidence records.
  - `GET /api/v1/evidence/{id}`: Evidence details with AI result and duplicate flags.
- **AI Assessment**:
  - `POST /api/v1/ai/analyze-image`: Standalone Gemini Vision analysis returning `FloodAssessment` with strict guardrails (no water depth inference).
  - `GET /api/v1/ai/status`: Gemini service status.
- **Geospatial**:
  - `GET /api/v1/geo/incidents`: GeoJSON FeatureCollection of flood incidents.
  - `GET /api/v1/geo/road-risks`: GeoJSON FeatureCollection of road segments with risk scores and blockage status.
- **Routes**:
  - `POST /api/v1/routes/calculate`: NetworkX Dijkstra dual-routing (plain shortest vs hazard-aware path avoiding segments with risk $\ge$ 80 or blocked).
  - `PATCH /api/v1/routes/segments/{id}/block`: Operator road closure toggle.
  - `GET /api/v1/routes/status`: Routing graph status.
- **Dashboard**:
  - `GET /api/v1/dashboard/kpis`: Real-time operator metrics.
  - `GET /api/v1/dashboard/timeline`: Recent dispatch events.
  - `GET /api/v1/dashboard/explainability/{id}`: Evidence factor breakdown & excluded road segments.
- **Weather**:
  - `GET /api/v1/weather`: Open-Meteo precipitation forecast with 10-minute cache and mandatory context disclaimer.
- **Facilities**:
  - `GET /api/v1/facilities/nearby`: Critical facilities (hospital, shelter, fire station) sorted by proximity.
