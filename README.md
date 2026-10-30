# GridBricks WindPulse: UK Wholesale Day-Ahead Renewable Generation & Accuracy Intelligence

A full-stack software application built for UK energy utilities participating in the wholesale Day-Ahead electricity market. The platform enables power procurement teams to inspect the latest wind generation forecasts available at day-ahead gate closure ($D-1$), quantify forecast errors against actual outturn generation, and size thermal procurement and balancing reserve buffers with quantified risk margins.

---

## Deployment & Repository Links

- **Live Frontend (Vercel):** [https://gridbricks-windpulse.vercel.app](https://gridbricks-windpulse.vercel.app)
- **Live Backend API (Render):** [https://gridbricks-backend.onrender.com](https://gridbricks-backend.onrender.com)
- **API Documentation (Swagger UI):** [https://gridbricks-backend.onrender.com/docs](https://gridbricks-backend.onrender.com/docs)
- **Anonymous GitHub Repository:** [https://github.com/anonymous-dev-774/kjhwr](https://github.com/anonymous-dev-774/kjhwr)

---

## Problem Statement & Domain Context

UK energy utilities must procure power in wholesale markets to serve consumer electricity demand. Power purchase decisions in the **UK Day-Ahead wholesale market** (EPEX SPOT and Nord Pool GB auctions) close around **11:00 UTC on day $D-1$** for power delivery across the 24 hours of day $D$.

Because wind generation is weather-dependent and variable:
1. **Procurement Teams Must Rely on Day-Ahead Forecasts:** Traders need to know how much thermal energy (e.g., CCGT gas or biomass) to buy in the day-ahead auction beyond expected wind output.
2. **Forecast Errors Create Financial Imbalance Exposure:**
   - **Over-forecasting wind (Shortfall):** The utility under-buys thermal power and must scramble to buy emergency balancing power at punitive system cashout prices in real time.
   - **Under-forecasting wind (Surplus):** The utility over-buys expensive thermal generation day-ahead and is forced to dump surplus wind into the balancing market at depressed prices.
3. **Strict Gate Closure Constraint:** When making bids at 11:00 UTC on day $D-1$, traders **must only use forecasts available at or before gate closure**. Forecasts published after gate closure are irrelevant to the day-ahead bid.

**GridBricks WindPulse** solves these challenges by providing:
- **Day-Ahead Procurement View:** Visualizes the exact forecast available at gate closure against actual outturn generation.
- **Quantitative Accuracy Evaluation:** Tracks MAE, RMSE, WAPE, Mean Bias Error (MBE), and error quantiles across January 2026.
- **Balancing Reserve Buffer Sizing:** Computes the statistical reserve cushion ($P_{90}$ or $P_{95}$ shortfall) required to guarantee consumer supply.
- **Data Explorer & Export:** Complete half-hourly/hourly audit log with one-click CSV export.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       Frontend: React 18 + Vite                              │
│       Tailwind CSS · Shadcn UI Components · Formik + Zod Validation          │
│              Recharts Visualizations · Lucide React Icons                   │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ HTTP / REST
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                       Backend: Python 3.12 + FastAPI                        │
│          Pydantic v2 · Pandas · NumPy · Analytics Engine · Uvicorn          │
├─────────────────────────────────────────────────────────────────────────────┤
│  Endpoints:                                                                 │
│  - GET /api/v1/dates                      - GET /api/v1/metrics/daily       │
│  - GET /api/v1/day-ahead                  - GET /api/v1/metrics/dist        │
│  - GET /api/v1/metrics/summary            - POST /api/v1/metrics/balancing  │
│  - GET /api/v1/metrics/hourly-profile     - POST /api/v1/sync               │
│  - GET /api/v1/export (CSV)                                                 │
└──────────────────┬──────────────────────────────────────┬───────────────────┘
                   │ SQL Queries                          │ HTTP Streams
┌──────────────────▼──────────────────┐   ┌───────────────▼───────────────────┐
│        SQLite Data Cache            │   │         Elexon BMRS API           │
│  - actual_wind (FUELHH WIND)        │   │  - FUELHH (30-min actuals)        │
│  - forecast_wind (WINDFOR)          │   │  - WINDFOR (hourly forecasts)     │
│  - sync_log                         │   │  Period: January 2026             │
└─────────────────────────────────────┘   └───────────────────────────────────┘
```

---

## File and Directory Structure

```
Gridbricks/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI entry point, lifespan, CORS
│   │   ├── config.py                  # Environment paths & market cutoff constants
│   │   ├── database.py                # SQLite schema, tables, connection manager
│   │   ├── schemas.py                 # Pydantic request & response models
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── dates.py               # GET /api/v1/dates (available dates & cutoffs)
│   │   │   ├── day_ahead.py           # GET /api/v1/day-ahead (aligned delivery schedule)
│   │   │   ├── metrics.py             # GET /api/v1/metrics/* (summary, profile, timeline, calc)
│   │   │   ├── sync.py                # POST /api/v1/sync (Elexon BMRS synchronization)
│   │   │   └── export.py              # GET /api/v1/export (CSV streaming download)
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── elexon_client.py       # Async HTTPX client for FUELHH & WINDFOR streams
│   │       ├── data_store.py          # Data access layer & D-1 cutoff alignment logic
│   │       └── analytics.py           # MAE, RMSE, MBE, WAPE, quantiles, and balancing engine
│   ├── data/
│   │   └── wind_data.db               # SQLite database pre-populated with Jan 2026 data
│   ├── scripts/
│   │   └── ingest_data.py             # Automated ingestion script for January 2026
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_aggregation.py       # Unit tests: 30-min actuals to hourly aggregation
│   │   ├── test_alignment.py         # Unit tests: D-1 gate cutoff & future exclusion
│   │   ├── test_metrics.py           # Unit tests: MAE, RMSE, WAPE, zero generation, calc
│   │   └── test_api.py               # Integration tests: FastAPI endpoints schema & 200s
│   ├── Dockerfile                     # Python 3.12 backend container
│   └── requirements.txt               # Backend dependencies
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ui/                    # Shadcn UI primitives (Card, Button, Badge,
│   │   │   │   ├── card.jsx           # Tabs, Input, Select, Table, Alert)
│   │   │   │   ├── button.jsx
│   │   │   │   ├── badge.jsx
│   │   │   │   ├── tabs.jsx
│   │   │   │   ├── input.jsx
│   │   │   │   ├── select.jsx
│   │   │   │   ├── table.jsx
│   │   │   │   └── alert.jsx
│   │   │   ├── Header.jsx             # Top bar, BMRS status badge, live sync trigger
│   │   │   ├── DayAheadView.jsx       # Section A: Day-Ahead View (Formik + Zod + Recharts)
│   │   │   ├── AccuracyView.jsx       # Section B: Quantitative Accuracy (KPIs + 3 Charts)
│   │   │   ├── BalancingView.jsx      # Section C: Risk & Balancing Calculator (Formik + Zod)
│   │   │   └── DataExplorerView.jsx   # Section D: Filterable Data Table & CSV Export
│   │   ├── lib/
│   │   │   └── utils.js               # Tailwind cn helper
│   │   ├── App.jsx                    # Root tabbed application shell
│   │   ├── index.css                  # Global Tailwind CSS styles
│   │   └── main.jsx                   # React 18 DOM mount
│   ├── Dockerfile                     # Multi-stage Node build + Nginx reverse proxy
│   ├── nginx.conf                     # Nginx routing and /api/ reverse proxy config
│   ├── package.json                   # React, Vite, Tailwind, Formik, Zod, Recharts
│   └── vite.config.js                 # Vite development proxy
├── docker-compose.yml                 # Unified single-command container orchestration
├── pytest.ini                         # Pytest configuration
├── vercel.json                        # Vercel deployment specification
├── Procfile                           # Heroku / Render deployment specification
├── DEMO_SCRIPT.md                     # Turn-by-turn video presentation script (< 10 mins)
└── README.md                          # Project documentation
```

---

## Core Domain Logic & Technical Methodology

### 1. Data Ingestion & Resolution Alignment
- **Actual Generation (`FUELHH`):** Filtered for `fuelType == "WIND"`. Delivered at half-hourly resolution ($48$ settlement periods per day). Because forecasts are hourly, the system groups `:00` (period $2k-1$) and `:30` (period $2k$) and calculates their arithmetic mean:
  $$\text{Actual}_{\text{hour } h} = \frac{\text{Actual}_{h:00} + \text{Actual}_{h:30}}{2}$$
- **Forecast Generation (`WINDFOR`):** Delivered at hourly resolution with individual `publishTime` timestamps.
- **Coverage:** December 31, 2025 through February 2, 2026 (ensuring all day-ahead decisions made in January 2026 for delivery in January 2026 are covered).

### 2. Day-Ahead Forecast Alignment Logic (Strict Gate Closure)
For any delivery day $D$:
1. The procurement decision is made on day $D - 1$.
2. The user selects a decision cutoff time $T_{\text{cutoff}}$ (default `11:00 UTC` for EPEX/Nord Pool GB auction gate closure; customizable to `09:30`, `12:00`, `15:30`, or `17:00`).
3. For each delivery hour $h \in [00:00, 23:00]$ on day $D$, the system queries:
   $$\text{Forecast}(h) = \operatorname{argmax}_{\text{publishTime} \le (D-1) \, T_{\text{cutoff}}} \Big( \text{generation} \Big)$$
4. **Strict Guarantee:** Any forecast with $\text{publishTime} > (D-1) \, T_{\text{cutoff}}$ is strictly excluded.

### 3. Quantitative Error Formulas
- **Forecast Error:** $e_i = F_i - A_i$ (positive = over-forecast / wind shortfall; negative = under-forecast / wind surplus).
- **Mean Absolute Error (MAE):** $\text{MAE} = \frac{1}{N}\sum_{i=1}^N |F_i - A_i|$
- **Root Mean Squared Error (RMSE):** $\text{RMSE} = \sqrt{\frac{1}{N}\sum_{i=1}^N (F_i - A_i)^2}$
- **Mean Bias Error (MBE):** $\text{MBE} = \frac{1}{N}\sum_{i=1}^N (F_i - A_i)$
- **Weighted Absolute Percentage Error (WAPE):**
  $$\text{WAPE} = \frac{\sum_{i=1}^N |F_i - A_i|}{\sum_{i=1}^N A_i} \times 100\%$$
- **Accuracy Rate:** $\max(0, 100 - \text{WAPE})\%$
- **Reserve Buffer Sizing:** Quantiles of shortfall $e_i^+ = \max(0, F_i - A_i)$ at $90\%$ and $95\%$ protection levels.

---

## How to Start the Application

### Option 1: Single-Command Docker Compose (Recommended)

Requires Docker and Docker Compose installed:

```bash
# Clone the repository
git clone https://github.com/anonymous-dev-774/kjhwr.git
cd kjhwr

# Build and start both backend and frontend containers
docker compose up --build
```

- **Frontend:** Open [http://localhost:3000](http://localhost:3000)
- **Backend API:** Open [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check:** Open [http://localhost:8000/health](http://localhost:8000/health)

---

### Option 2: Local Development Setup

#### Backend Setup:
```bash
# Create and activate Python virtual environment
python3 -m venv backend/venv
source backend/venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# (Optional) Re-run data ingestion from Elexon BMRS if desired:
# python backend/scripts/ingest_data.py

# Run backend unit tests
pytest -v

# Start FastAPI server
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

#### Frontend Setup:
```bash
# In a new terminal, navigate to frontend
cd frontend

# Install dependencies
npm install

# Start Vite dev server with proxy to backend
npm run dev
```

Visit [http://localhost:3000](http://localhost:3000).

---

## Running the Automated Test Suite

The test suite validates response parsing, 30-minute to hourly aggregation, gate closure cutoff exclusion, statistical error calculations, and API contracts:

```bash
pytest -v
```

Output:
```
backend/tests/test_aggregation.py::test_hourly_aggregation_two_half_hours PASSED
backend/tests/test_aggregation.py::test_hourly_aggregation_single_half_hour PASSED
backend/tests/test_aggregation.py::test_hourly_aggregation_missing_data PASSED
backend/tests/test_alignment.py::test_forecast_alignment_selects_latest_before_cutoff PASSED
backend/tests/test_alignment.py::test_forecast_alignment_with_later_cutoff PASSED
backend/tests/test_alignment.py::test_forecast_alignment_strictly_excludes_future_forecasts PASSED
backend/tests/test_api.py::test_health_endpoint PASSED
backend/tests/test_api.py::test_dates_endpoint PASSED
backend/tests/test_api.py::test_day_ahead_endpoint PASSED
backend/tests/test_api.py::test_metrics_summary_endpoint PASSED
backend/tests/test_api.py::test_hourly_profile_endpoint PASSED
backend/tests/test_api.py::test_distribution_endpoint PASSED
backend/tests/test_api.py::test_export_endpoint PASSED
backend/tests/test_metrics.py::test_accuracy_metrics_calculation PASSED
backend/tests/test_metrics.py::test_zero_generation_and_empty_dataset PASSED
backend/tests/test_metrics.py::test_balancing_risk_calculator PASSED

======================== 16 passed, 1 warning in 1.65s =========================
```

---

## Deployment Guide

### Frontend Deployment (Vercel)
1. Push repository to GitHub.
2. In Vercel, import the repository with Root Directory set to `./`.
3. Vercel automatically detects `vercel.json` and builds `frontend/`.
4. Ensure the backend URL in `vercel.json` points to your deployed backend instance.

### Backend Deployment (Render / Heroku)
1. In Render or Heroku, create a Web Service pointing to this repository.
2. Build Command: `pip install -r backend/requirements.txt`
3. Start Command: `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
4. Environment Variables:
   - `PYTHONPATH=.`
   - `SQLITE_DB_PATH=backend/data/wind_data.db`

---

## Acknowledgment of AI Tools Used

In compliance with the assessment guidelines, AI assistance (Google Antigravity / Gemini) was utilized during the development of this project for:
- Researching Elexon BMRS API data structures and endpoint specifications.
- Assisting in the scaffolding of the React and FastAPI boilerplate.
- Drafting unit test cases for statistical edge cases and alignment logic.
- Refining the user interface design with Tailwind CSS and Recharts styling.
All business logic, market alignment algorithms, error calculations, and application designs were thoroughly reviewed, validated, and tested against actual Elexon January 2026 market data.
