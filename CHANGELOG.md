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

## [Phase 1] - Initial Skeleton
- **System**:
  - `GET /health`: Health status, disclaimer, mock_ai flag.
  - `WS /ws/incidents`: Real-time incident & routing telemetry stream.
- **Auth**:
  - `GET /api/v1/auth/me`: Current authenticated user profile.
- **Incidents**:
  - `GET /api/v1/incidents`: List incident reports with pagination.
- **Evidence**:
  - `GET /api/v1/evidence`: List submitted evidence records.
- **AI**:
  - `GET /api/v1/ai/status`: Gemini service status and vision guardrail check.
- **Geo**:
  - `GET /api/v1/geo/incidents`: GeoJSON FeatureCollection of flood incidents.
  - `GET /api/v1/geo/road-risks`: GeoJSON FeatureCollection of road risk segments.
- **Routes**:
  - `GET /api/v1/routes/status`: Routing engine status and disclaimer.
- **Dashboard**:
  - `GET /api/v1/dashboard/kpis`: Operator overview metric counts.
