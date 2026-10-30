# GridBricks WindPulse: UK Wholesale Day-Ahead Renewable Generation & Accuracy Intelligence

A full-stack software application built for UK energy utilities participating in the wholesale Day-Ahead electricity market. The platform enables power procurement teams to inspect the latest wind generation forecasts available at day-ahead gate closure ($D-1$), quantify forecast errors against actual outturn generation, and size thermal procurement and balancing reserve buffers with quantified risk margins.

Powered by **Neon Serverless PostgreSQL** via **SQLAlchemy** and **Psycopg 3**.

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
│          SQLAlchemy 2.0 · Psycopg 3 · Pydantic v2 · Pandas · NumPy          │
├─────────────────────────────────────────────────────────────────────────────┤
│  Endpoints:                                                                 │
│  - GET /api/v1/dates                      - GET /api/v1/metrics/daily       │
│  - GET /api/v1/day-ahead                  - GET /api/v1/metrics/dist        │
│  - GET /api/v1/metrics/summary            - POST /api/v1/metrics/balancing  │
│  - GET /api/v1/metrics/hourly-profile     - POST /api/v1/sync               │
│  - GET /api/v1/export (CSV)                                                 │
└──────────────────┬──────────────────────────────────────┬───────────────────┘
                   │ Pooled SQL Connection                │ HTTP Streams
┌──────────────────▼──────────────────┐   ┌───────────────▼───────────────────┐
│       Neon Serverless PostgreSQL    │   │         Elexon BMRS API           │
│  - actual_wind (FUELHH WIND)        │   │  - FUELHH (30-min actuals)        │
│  - forecast_wind (WINDFOR)          │   │  - WINDFOR (hourly forecasts)     │
│  - sync_log                         │   │  Period: January 2026             │
│  (Indexed & Idempotent Upserts)     │   │                                   │
└─────────────────────────────────────┘   └───────────────────────────────────┘
```

---

## File and Directory Structure

```
Gridbricks/
├── .dockerignore                       # Docker build exclusions
├── .env.example                        # Template for Neon PostgreSQL DATABASE_URL
├── .gitignore                          # Git exclusions (no db files or credentials)
├── docker-compose.yml                  # Root container orchestration with Neon env
├── package.json                        # Root CLI shortcuts (server:start, build, etc.)
├── Procfile                            # Heroku / Render deployment specification
├── pytest.ini                          # Pytest configuration
├── vercel.json                         # Vercel deployment specification
├── DEMO_SCRIPT.md                      # Turn-by-turn video presentation script (< 10 mins)
├── README.md                           # Comprehensive documentation
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                     # FastAPI entry point, lifespan, CORS
│   │   ├── config.py                   # Neon DATABASE_URL loader & market constants
│   │   ├── database.py                 # SQLAlchemy engine, pooled session manager
│   │   ├── models.py                   # SQLAlchemy models (ActualWind, ForecastWind, SyncLog)
│   │   ├── schemas.py                  # Pydantic request & response models
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── dates.py                # GET /api/v1/dates (available dates & cutoffs)
│   │   │   ├── day_ahead.py            # GET /api/v1/day-ahead (aligned delivery schedule)
│   │   │   ├── metrics.py              # GET /api/v1/metrics/* (summary, profile, timeline, calc)
│   │   │   ├── sync.py                 # POST /api/v1/sync (Elexon BMRS synchronization)
│   │   │   └── export.py               # GET /api/v1/export (CSV streaming download)
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── elexon_client.py        # Async HTTPX client for FUELHH & WINDFOR streams
│   │       ├── data_store.py           # PostgreSQL data access & idempotent upserts
│   │       └── analytics.py            # MAE, RMSE, MBE, WAPE, quantiles, and balancing engine
│   ├── scripts/
│   │   └── ingest_data.py              # Automated ingestion script for January 2026
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_aggregation.py        # Unit tests: 30-min actuals to hourly aggregation
│   │   ├── test_alignment.py          # Unit tests: D-1 gate cutoff & future exclusion
│   │   ├── test_metrics.py            # Unit tests: MAE, RMSE, WAPE, zero generation, calc
│   │   └── test_api.py                # Integration tests: FastAPI endpoints schema & 200s
│   ├── Dockerfile                      # Python 3.12 backend container
│   └── requirements.txt                # Backend dependencies (SQLAlchemy, Psycopg 3, etc.)
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── ui/                     # Shadcn UI primitives (Card, Button, Badge,
    │   │   │   ├── card.jsx            # Tabs, Input, Select, Table, Alert)
    │   │   │   ├── button.jsx
    │   │   │   ├── badge.jsx
    │   │   │   ├── tabs.jsx
    │   │   │   ├── input.jsx
    │   │   │   ├── select.jsx
    │   │   │   ├── table.jsx
    │   │   │   └── alert.jsx
    │   │   ├── Header.jsx              # Top bar, BMRS status badge, live sync trigger
    │   │   ├── DayAheadView.jsx        # Section A: Day-Ahead View (Formik + Zod + Recharts)
    │   │   ├── AccuracyView.jsx        # Section B: Quantitative Accuracy (KPIs + 3 Charts)
    │   │   ├── BalancingView.jsx       # Section C: Risk & Balancing Calculator (Formik + Zod)
    │   │   └── DataExplorerView.jsx    # Section D: Filterable Data Table & CSV Export
    │   ├── lib/
    │   │   └── utils.js                # Tailwind cn helper
    │   ├── App.jsx                     # Root tabbed application shell
    │   ├── index.css                   # Global Tailwind CSS styles
    │   └── main.jsx                    # React 18 DOM mount
    ├── Dockerfile                      # Multi-stage Node build + Nginx reverse proxy
    ├── nginx.conf                      # Nginx routing and /api/ reverse proxy config
    ├── package.json                    # React, Vite, Tailwind, Formik, Zod, Recharts
    └── vite.config.js                  # Vite development proxy
```

---

## Database Architecture: Neon Serverless PostgreSQL

The application exclusively uses **Neon PostgreSQL** as its sole data tier. SQLite has been completely removed.

### Key Database Features:
1. **Pooled Connection String:** Configured via `DATABASE_URL` using Neon's connection pooler (`ep-...-pooler...`) with `sslmode=require`.
2. **Serverless Connection Health:** Configured with `pool_pre_ping=True` and `pool_recycle=300` in SQLAlchemy to gracefully recover from serverless scale-to-zero wakeups.
3. **Idempotent Data Ingestion:** Uses PostgreSQL native upserts:
   ```sql
   INSERT INTO actual_wind (...) VALUES (...)
   ON CONFLICT (start_time) DO UPDATE SET ...;

   INSERT INTO forecast_wind (...) VALUES (...)
   ON CONFLICT (publish_time, start_time) DO UPDATE SET ...;
   ```
   Repeated synchronizations never create duplicate records.
4. **Credential Security:** Database credentials are kept strictly server-side in `.env` and are never exposed to the frontend.

---

## Root CLI Shortcuts (`npm run ...`)

The root `package.json` provides single-command shortcuts for all developer workflows:

| Command | Action |
| :--- | :--- |
| `npm run server:start` | Starts the FastAPI backend production server |
| `npm run server:start:show` | Starts the FastAPI backend server with `--reload` and live logs |
| `npm run server:build` | Creates Python virtual environment and installs backend dependencies |
| `npm run server:test` | Executes the complete `pytest` automated test suite |
| `npm run server:ingest` | Runs the ingestion pipeline to seed January 2026 data into Neon |
| `npm run client:start` | Starts the Vite React frontend development server on `:3000` |
| `npm run client:build` | Builds the production React bundle in `frontend/dist/` |
| `npm run dev` | Runs both Backend and Frontend concurrently in one terminal |
| `npm run install:all` | Installs dependencies for both Backend and Frontend |
| `npm run docker:up` | Boots the application using Docker Compose |
| `npm run docker:down` | Stops Docker Compose containers |

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
3. For each delivery hour $h \in [00:00, 23:00]$ on day $D$, the system queries Neon PostgreSQL:
   ```sql
   SELECT publish_time, generation 
   FROM forecast_wind 
   WHERE start_time = :hour_target AND publish_time <= :cutoff_datetime
   ORDER BY publish_time DESC 
   LIMIT 1;
   ```
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

### Option 1: Using Root NPM Scripts (Fastest)

```bash
# 1. Install dependencies
npm run install:all

# 2. Start both Backend & Frontend together
npm run dev
```

- **Frontend:** [http://localhost:3000](http://localhost:3000)
- **Backend API:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

### Option 2: Single-Command Docker Compose

```bash
# Make sure .env has your DATABASE_URL
docker compose up --build
```

- **Frontend:** [http://localhost:3000](http://localhost:3000)
- **Backend API:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Running the Automated Test Suite

```bash
npm run server:test
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
backend/tests/test_day_ahead_endpoint PASSED
backend/tests/test_metrics_summary_endpoint PASSED
backend/tests/test_hourly_profile_endpoint PASSED
backend/tests/test_distribution_endpoint PASSED
backend/tests/test_export_endpoint PASSED
backend/tests/test_metrics.py::test_accuracy_metrics_calculation PASSED
backend/tests/test_metrics.py::test_zero_generation_and_empty_dataset PASSED
backend/tests/test_metrics.py::test_balancing_risk_calculator PASSED

======================== 16 passed, 1 warning =========================
```

---

## Acknowledgment of AI Tools Used

In compliance with the assessment guidelines, AI assistance (Google Antigravity / Gemini) was utilized during development for:
- Researching Elexon BMRS API data structures and endpoint specifications.
- Scaffolding the React and FastAPI boilerplate.
- Designing unit test cases for statistical edge cases and alignment logic.
- Refining the user interface design with Tailwind CSS and Recharts styling.
All business logic, market alignment algorithms, error calculations, and application designs were thoroughly reviewed, validated, and tested against actual Elexon January 2026 market data.
