# AFTERFLOW

> **"When roads fail, intelligence takes over."**  
> *AI-powered urban flood intelligence and hazard-aware route optimization.*

---

## 🌊 Overview & Core Workflow

AFTERFLOW is a prototype decision-support system designed to address urban flash-flooding, submerged road corridors, and uncoordinated emergency transit. It fuses ground citizen evidence with Google Gemini computer vision, validates reports through spatio-temporal and perceptual duplicate correlation, computes uncertainty-aware TrustScores, and executes hazard-penalized Dijkstra routing to navigate vehicles safely around waterlogged bottlenecks.

```
┌─────────────────┐      ┌───────────────────────────┐      ┌─────────────────────────┐      ┌─────────────────────────┐
│ 01. VISION      │      │ 02. CORRELATION           │      │ 03. TRUSTSCORE & RISK   │      │ 04. HAZARD ROUTING      │
│ Gemini AI       │ ───► │ pHash + Spatial-Temporal  │ ───► │ Multi-Factor Fusion     │ ───► │ NetworkX Dijkstra       │
│ Surface bounds, │      │ Deduplication of images & │      │ Trust = 0.25G + 0.20Tm  │      │ Exclude blocked/risk>=80│
│ visible water,  │      │ clustering of nearby      │      │         + 0.35V + 0.20I │      │ Cost = Dist + λ * Risk  │
│ strict limits   │      │ independent citizen alerts│      │ Risk = 0.4S+0.25P+0.2E  │      │ Reroutes to safe bypass │
└─────────────────┘      └───────────────────────────┘      └─────────────────────────┘      └─────────────────────────┘
```

---

## 🏛️ System Architecture

```
                                  +-------------------------------------------------+
                                  |            AFTERFLOW CLIENT (Next.js)           |
                                  |  - Mobile Ground Reporting (/report)            |
                                  |  - Live Hazard Leaflet Map (/map)               |
                                  |  - Hazard-Aware Routing Canvas (/routes)        |
                                  |  - Operator Command Console (/dashboard)        |
                                  +-------------------------------------------------+
                                                     ▲            │
                                    HTTP API / REST  │            │  WebSocket Telemetry
                                  (JSON Contract v1) │            │  (/ws/incidents)
                                                     │            ▼
                                  +-------------------------------------------------+
                                  |             FASTAPI BACKEND MONOLITH            |
                                  |                                                 |
                                  |  [ Routers: /api/v1 ]                           |
                                  |  ├── /auth: JWT Role-Based Auth (Citizen/Op)    |
                                  |  ├── /incidents: Ground Reports & Evidence      |
                                  |  ├── /ai: Gemini Vision Assessment (Guardrailed)|
                                  |  ├── /geo: GeoJSON FeatureCollections           |
                                  |  ├── /routes: Dijkstra Hazard-Aware Routing     |
                                  |  ├── /weather: Open-Meteo Precipitation Context |
                                  |  └── /dashboard: Real-Time Operator KPIs        |
                                  +-------------------------------------------------+
                                            │               │               │
                     ┌──────────────────────┴───────┐       │       ┌───────┴──────────────────────┐
                     ▼                              ▼       ▼       ▼                              ▼
      +-----------------------------+   +-----------------------+   +------------------------------+
      |      PostGIS / Postgres     |   |   Google Gemini AI    |   |     NetworkX In-Memory       |
      | - Spatial Indexing (GIST)   |   | - google-genai SDK    |   | - Seeded Agra Urban Graph    |
      | - Append-only Verifications |   | - Strict JSON schema  |   | - Snap origin/dest to nodes  |
      | - Road Segments & Inundation|   | - Depth Hallucination |   | - Dynamic Edge Weighting     |
      | - Critical Facilities       |   |   Guardrails          |   | - Subgraph Pruning & Detours |
      +-----------------------------+   +-----------------------+   +------------------------------+
```

---

## ⚙️ Tech Stack

- **Backend:** Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2, GeoAlchemy2, Alembic, PostgreSQL + PostGIS (Modular Monolith)
- **Frontend:** Next.js 14 (App Router), TypeScript, Tailwind CSS, Leaflet + OpenStreetMap
- **AI Vision:** Google Gemini API via `google-genai` (Structured JSON output mode)
- **Routing Engine:** NetworkX (Hazard-penalized Dijkstra)
- **Realtime:** FastAPI WebSockets (`/ws/incidents`)
- **Weather Context:** Open-Meteo API (10-minute in-memory cache)
- **Storage:** Cloudinary SDK with inline base64 fallback
- **Testing:** Pytest & pytest-asyncio

---

## 🔒 Hard Rules & Ethical Guardrails

1. **Advisory Decision-Support Only:** AFTERFLOW is a prototype decision-support tool, **never an official emergency dispatch service**. Routes are never labeled "guaranteed safe". Prominent disclaimers, freshness timestamps, and limitations are shown across all screens.
2. **Strict AI Depth Boundaries:** AI models can assess visible water, reflections, and submerged tire bounds from 2D photos, but **must NEVER infer exact water depth**. The system returns explicit technical limitations with every assessment.
3. **Hazard Priority Decoupled from Evidence Confidence:** Priority Risk ($0.40S + 0.25P + 0.20E + 0.15C$) is maintained separately from evidence TrustScore ($0.25G + 0.20Tm + 0.35V + 0.20I$) so operators know both *how severe* an incident is and *how verified* it is.
4. **Deterministic Simulation Tags:** All seeded/synthetic demo data is explicitly tagged `is_simulated=true` and rendered with a distinct purple "Simulated" badge.
5. **Local Routing Resilience:** Uses an in-memory cached road graph (centered in Agra, India: Lat 27.1767, Lng 78.0081). Does not depend on live road network downloads during demos.

---

## 🚀 Quickstart & Installation

### 1. Backend Setup
```powershell
cd backend
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
```

To run demo seeding:
```powershell
python scripts/seed_demo.py
```

To start the FastAPI backend:
```powershell
python -m uvicorn app.main:app --reload --port 8000
```
Backend Swagger Documentation: `http://localhost:8000/docs`  
Health Check: `http://localhost:8000/health`

### 2. Frontend Setup
```powershell
cd frontend
npm install
npm run dev
```
Open `http://localhost:3000` in your browser.

### 3. Docker Compose (Full Stack with PostGIS)
```powershell
docker-compose up --build
```

---

## 🧪 Running Acceptance Tests

Run the full pytest suite covering AI guardrails, duplicate detection, TrustScore progression, Dijkstra rerouting, and performance targets:

```powershell
cd backend
python -m pytest tests/ -v
```

---

## ⏱️ 3-Minute Hackathon Demo Script

| Time | Stage | Action / Talking Point |
|---|---|---|
| **0:00 - 0:30** | **Problem Statement** | "During sudden monsoon urban floods, standard map GPS apps send drivers directly into flooded underpasses because they lack real-time ground truth. Citizen reports are noisy, duplicated, and unverified. Enter AFTERFLOW: *When roads fail, intelligence takes over.*" |
| **0:30 - 1:00** | **Citizen Report & AI Vision** | Open `/report`. Upload a street flood photo. Show the live upload pipeline: image format validated, pHash computed, and Gemini AI returning surface water classification, coverage, and strict limitations stating water depth cannot be measured from 2D photos. |
| **1:00 - 1:40** | **Corroboration & TrustScore** | Open `/incidents/[id]`. Show how a single report starts as `Unverified` (TrustScore ~35). Demonstrate how 2 nearby independent citizen reports within 200m boost the score to `Probable` and then `Strong Evidence` (84/100). Show the duplicate detector flagging identical photos. |
| **1:40 - 2:20** | **Hazard Routing Engine** | Navigate to `/routes`. Show the standard shortest route through MG Road (grey dashed line) passing through the flooded zone. Toggle 'Avoid High-Risk Roads'. Watch the Dijkstra engine instantly exclude the high-risk edge ($\ge 80$) and calculate a cyan safe detour via Civil Lines West Bypass, saving 88% hazard exposure in $< 0.1$s. |
| **2:20 - 2:50** | **Operator Command Center** | Switch to `/dashboard`. Inspect the real-time queue sorted by Priority Risk ($0.40S + 0.25P + 0.20E + 0.15C$). Show proximity to critical emergency facilities (hospital & flood shelters). Toggle a manual road block; observe live WebSocket broadcast alerting all active navigation units. |
| **2:50 - 3:00** | **Closing & Vision** | "AFTERFLOW bridges citizen ground evidence, vision AI guardrails, and dynamic graph optimization so cities remain navigable when disaster strikes. *When roads fail, intelligence takes over.*" |

---

## 📋 Pre-Demo Checklist

- [x] Database seeded with `python scripts/seed_demo.py` (1 Operator, 3 Citizens, 4 Facilities, 3 Correlated reports, 1 Duplicate test).
- [x] `MOCK_AI=true` tested for zero-latency, network-independent local presentations.
- [x] FastAPI WebSocket server verified on `ws://localhost:8000/ws/incidents`.
- [x] Tested route recalculation detour `< 2.0s`.
- [x] Screen recording backup captured for contingency.

---

## 📄 License
MIT License. Built for the 48-Hour Hackathon Prototype Challenge.
