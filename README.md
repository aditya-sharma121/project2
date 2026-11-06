<div align="center">

# 🌊 AFTERFLOW
### *When roads fail, intelligence takes over.*

**AI-Powered Urban Flood Intelligence & Hazard-Aware Route Optimization**

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Frontend-Next.js%2014-black?style=for-the-badge&logo=next.js&logoColor=white)](https://nextjs.org)
[![Gemini AI](https://img.shields.io/badge/AI-Google%20Gemini%20Vision-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev)
[![PostGIS](https://img.shields.io/badge/Spatial-PostgreSQL%20%2B%20PostGIS-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgis.net)
[![NetworkX](https://img.shields.io/badge/Routing-NetworkX%20Dijkstra-FF6F00?style=for-the-badge&logo=python&logoColor=white)](https://networkx.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

<p align="center">
  <a href="#-the-problem">The Problem</a> •
  <a href="#-how-it-works-4-step-pipeline">How It Works</a> •
  <a href="#-core-features">Features</a> •
  <a href="#-system-architecture">Architecture</a> •
  <a href="#-quickstart--run-locally">Quickstart</a> •
  <a href="#-3-minute-demo-pitch-script">Demo Script</a> •
  <a href="#-responsible-ai--disclaimers">Disclaimers</a>
</p>

---

</div>

## 🚨 The Problem

During sudden urban flash floods and heavy monsoon downpours, standard GPS mapping applications lead drivers and emergency vehicles straight into **submerged underpasses and impassable roads**. 

Why does this happen?
1. **Satellite and road sensors lag behind** by hours, while flash flooding happens in minutes.
2. **Citizen alerts on social media are chaotic, unverified, and filled with duplicate images**.
3. **No existing navigation app dynamically adjusts routing costs based on flood hazard severity and verified ground confidence**.

**AFTERFLOW bridges this gap.** It turns everyday citizen smartphone photos into verified urban flood intelligence, penalizes hazardous flooded corridors using Dijkstra graph theory, and calculates safe reroutes in real-time.

---

## ⚡ How It Works: The 4-Step Pipeline

```
  ┌────────────────┐       ┌────────────────┐       ┌────────────────┐       ┌────────────────┐
  │   01. VISION   │       │02. CORRELATION │       │03. TRUSTSCORE  │       │  04. ROUTING   │
  │                │  ──►  │                │  ──►  │   & RISK       │  ──►  │                │
  │ Gemini Vision  │       │ pHash & Spatio-│       │ Multi-Factor   │       │ NetworkX       │
  │ Photo Analysis │       │ Temporal Match │       │ Uncertainty    │       │ Hazard Avoidance│
  └────────────────┘       └────────────────┘       └────────────────┘       └────────────────┘
```

### 1️⃣ Vision: Guardrailed AI Image Assessment
A citizen snaps a photo of water on a street. **Google Gemini Vision** immediately analyzes the visible scene:
- Detects standing/flowing water, submerged tires, and road surface coverage percentage.
- **Strict Guardrail Rule:** The AI **never guesses water depth** (optical refraction and perspective make depth estimation from 2D photos dangerous). It outputs clear technical limitations with every scan.

### 2️⃣ Correlation: Perceptual Deduplication
To prevent bot spam, panic re-uploads, or malicious tampering:
- Every image is processed through **SHA-256** and **Perceptual Hashing (pHash)**.
- If two users submit identical photos or visually similar angles (Hamming distance $\le 8$), they are flagged as duplicates and do *not* count as independent evidence.

### 3️⃣ TrustScore & Decoupled Risk Prioritization
AFTERFLOW calculates two strictly separated metrics:
- **TrustScore ($0 \to 100$):** *How reliable is the evidence?*  
  $$\text{TrustScore} = 0.25G + 0.20Tm + 0.35V + 0.20I$$
  - **$G$ (Geographic Agreement):** Proximity and density of nearby corroborating reports within $200\text{m}$.
  - **$Tm$ (Temporal Agreement):** Freshness of the alert (decays with time).
  - **$V$ (Visual Quality):** AI confidence, visible water presence, and road coverage.
  - **$I$ (Independent Sources):** Bonus for alerts submitted by distinct, non-duplicate citizen accounts.
  - *Labels:* **Unverified** ($0-39$) $\to$ **Probable** ($40-69$) $\to$ **Strong evidence** ($70-84$) $\to$ **High-confidence evidence** ($85-100$).
- **Priority Risk Score ($0 \to 100$):** *How dangerous is this to urban infrastructure?*  
  $$\text{Risk} = 0.40S + 0.25P + 0.20E + 0.15C$$
  Evaluates flood severity ($S$), road class importance ($P$), proximity to emergency facilities like hospitals ($E$), and evidence TrustScore ($C$).

### 4️⃣ Hazard-Aware Routing Engine
The in-memory **NetworkX Dijkstra** engine recalculates routes in milliseconds:
- **Exclusion Threshold:** Road segments with $\text{Risk} \ge 80$ or manual operator blockages are completely pruned from the navigation graph.
- **Dynamic Cost Function:**
  $$\text{Edge Cost} = \text{Distance (m)} + (\lambda \times \text{Risk Score})$$
  Vehicles are gently steered through elevated, safe alternative bypasses instead of submerged corridors.

---

## ✨ Core Features

| Feature | Description | Target User |
|---|---|---|
| 📱 **Mobile Ground Reporting** | One-tap upload, automatic GPS location, instant Gemini AI analysis card with limitations, and upload progress tracker. | Citizens & Commuters |
| 🗺️ **Live Leaflet Hazard Map** | Color-coded severity markers (Green/Yellow/Red), confidence-scaled pulse rings, road inundation polylines, and critical facility markers. | Public & First Responders |
| 🧭 **Hazard Route Planner** | Side-by-side comparison between **Direct Shortest Path** (grey dashed) and **Safe Hazard-Aware Path** (cyan solid) with avoided segment reasons and detour metrics. | Drivers, Ambulances & Responders |
| 🛡️ **Operator Command Console** | Live incident queue sorted by Priority Risk, manual road closure toggles (triggers live reroutes across all users), and explainability factor drawers. | Disaster Management Authorities |
| 🌦️ **Real-time Weather Context** | Live precipitation and rainfall probability via Open-Meteo API (10-minute in-memory cache) with context disclaimers. | Dispatchers & Operators |
| ⚡ **Live WebSocket Telemetry** | Auto-reconnecting `/ws/incidents` stream for real-time map marker and road blockage synchronization without page reloads. | All Connected Clients |

---

## 🏛️ System Architecture

```
                                      +---------------------------------------------+
                                      |         AFTERFLOW CLIENT (Next.js 14)       |
                                      |  • /report   • /map   • /routes   • /dashboard |
                                      +---------------------------------------------+
                                                       ▲            │
                                      HTTP / JSON REST │            │  WebSocket Telemetry
                                            (/api/v1)  │            │  (/ws/incidents)
                                                       │            ▼
                                      +---------------------------------------------+
                                      |           FASTAPI BACKEND MONOLITH          |
                                      |                                             |
                                      |  Core Routers:                              |
                                      |  ├── /auth: JWT RBAC (Citizen & Operator)   |
                                      |  ├── /incidents: Reports & Evidence Pipeline|
                                      |  ├── /ai: Gemini Vision Guardrailed Engine  |
                                      |  ├── /geo: GeoJSON FeatureCollections       |
                                      |  ├── /routes: Dijkstra Hazard-Aware Routing |
                                      |  ├── /weather: Open-Meteo Cached Forecast   |
                                      |  └── /dashboard: Operator KPIs & Telemetry  |
                                      +---------------------------------------------+
                                             │               │               │
                     ┌───────────────────────┴──────┐        │        ┌──────┴───────────────────────┐
                     ▼                              ▼        ▼        ▼                              ▼
      +-----------------------------+   +------------------------+   +-------------------------------+
      |      PostGIS / Postgres     |   |    Google Gemini AI    |   |      NetworkX In-Memory       |
      | • Spatial Geography Points  |   | • google-genai SDK     |   | • Seeded Agra Urban Network   |
      | • GIST Spatial Indexes      |   | • Structured JSON      |   | • Dynamic Edge Hazard Weights |
      | • Append-Only Verifications |   | • Depth Guardrails     |   | • Subgraph Pruning & Detours  |
      +-----------------------------+   +------------------------+   +-------------------------------+
```

---

## 🚀 Quickstart & Run Locally

### Prerequisites
- Python 3.10+ (tested with Python 3.11 & 3.13)
- Node.js 18+ & npm

---

### Step 1: Clone the Repository
```bash
git clone https://github.com/aditya-sharma121/project2.git
cd project2
```

---

### Step 2: Backend Setup
```bash
cd backend

# Create & activate a virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
copy .env.example .env   # (Windows)
# cp .env.example .env   # (Linux/macOS)
```

#### Run Demo Seeder (Seeds Users, Facilities, Correlated Reports & Graph)
```bash
python scripts/seed_demo.py
```

#### Start FastAPI Backend Server
```bash
python -m uvicorn app.main:app --reload --port 8000
```
- API Docs (Swagger UI): `http://localhost:8000/docs`
- Healthcheck Endpoint: `http://localhost:8000/health`

---

### Step 3: Frontend Setup
Open a new terminal:
```bash
cd frontend

# Install packages
npm install

# Start Next.js Development Server
npm run dev
```
Open **`http://localhost:3000`** in your browser.

---

### 🔑 Demo Login Credentials (Pre-seeded)

For fast judging and evaluations, demo accounts are pre-configured:

| Role | Email | Password | Access Level |
|---|---|---|---|
| **Emergency Operator** | `operator@afterflow.gov` | `operatorpassword` | Full Command Center, Manual Road Blockades, Status Triage |
| **Citizen Reporter** | `citizen1@agra.org` | `citizenpassword` | Ground Reporting & Route Calculation |

*(Tip: The `/login` page features 1-click quick-fill buttons for both roles!)*

---

## 🧪 Running Acceptance Tests

Run the complete test suite verifying AI guardrails, duplicate detection, TrustScore correlation, Dijkstra rerouting, and performance thresholds:

```bash
cd backend
python -m pytest tests/ -v
```

**Results:**
```
tests/test_acceptance.py::test_decision_support_disclaimer_health PASSED
tests/test_acceptance.py::test_ai_flood_assessment_mock_modes PASSED
tests/test_acceptance.py::test_invalid_upload_validation_rejected PASSED
tests/test_acceptance.py::test_duplicate_image_deduplication PASSED
tests/test_acceptance.py::test_trust_score_multi_report_progression PASSED
tests/test_acceptance.py::test_hazard_priority_vs_confidence_decoupling PASSED
tests/test_acceptance.py::test_routing_engine_high_risk_exclusion PASSED
tests/test_acceptance.py::test_performance_targets PASSED (API < 1s, Route < 2s)
tests/test_health.py::test_health_check_endpoint PASSED
tests/test_health.py::test_error_response_format_404 PASSED
tests/test_health.py::test_api_v1_subroutes_exist PASSED
======================= 11 passed in 6.55s =======================
```

---

## ⏱️ 3-Minute Demo Pitch Script (For Judges & Evaluators)

| Time | Screen | Talking Points |
|---|---|---|
| **0:00 - 0:30** | Landing Page (`/`) | *"Standard navigation apps are blind to flash floods. Drivers blindly enter flooded underpasses because satellite data is hours old and citizen alerts are noisy. AFTERFLOW fixes this: When roads fail, intelligence takes over."* |
| **0:30 - 1:00** | Citizen Report (`/report`) | *Show uploading a waterlogged street photo. Point out the live validation: 5MB limit check, pHash fingerprinting, and Gemini Vision outputting visible water coverage while strictly refusing to hallucinate water depth.* |
| **1:00 - 1:40** | Incident Detail (`/incidents/[id]`) | *Show the multi-factor TrustScore. Explain how an initial solo report begins as `Unverified` (35/100). As 2 nearby citizens corroborate within 200m, the score climbs to `Probable` and then `Strong evidence` (84/100). Show identical photo deduplication in action.* |
| **1:40 - 2:20** | Route Planner (`/routes`) | *Show standard shortest route directly crossing flooded MG Road (grey dashed). Toggle 'Avoid High-Risk Roads' — the NetworkX Dijkstra engine excludes the inundated segment and computes a safe cyan bypass in under 0.1 seconds.* |
| **2:20 - 2:50** | Operator Console (`/dashboard`) | *Show the real-time queue sorted by Priority Risk ($0.40S + 0.25P + 0.20E + 0.15C$). Show proximity to hospitals and flood shelters. Toggle a manual road block to demonstrate instant WebSocket rerouting across all active clients.* |
| **2:50 - 3:00** | Conclusion | *"AFTERFLOW transforms scattered citizen photos into dynamic, hazard-resilient routes that save lives and emergency vehicles. When roads fail, intelligence takes over."* |

---

## 🛡️ Responsible AI & Ethical Guardrails

- ⚠️ **Advisory Prototype Disclaimer:** AFTERFLOW is an experimental decision-support prototype and **never an official emergency dispatch service**. Routes are advisory calculations and **never labeled "guaranteed safe"**. Users must always obey police barriers and local civil defense evacuation directives.
- 🚫 **No Water Depth Hallucination:** Visual perspective cannot reliably determine hydrological depth from a single 2D camera angle. Gemini AI is strictly bounded to visible surface water coverage only.
- 🟣 **Simulation Transparency:** All synthetic test data and seeded incidents are marked with `is_simulated=true` and display a clear purple `[SIMULATED]` tag in the user interface.

---

<div align="center">

**Built with ❤️ for the 48-Hour Urban Resilience Hackathon Challenge.**  
*Repository:* [github.com/aditya-sharma121/project2](https://github.com/aditya-sharma121/project2)

</div>
