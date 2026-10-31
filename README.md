# GridBricks WindPulse

GridBricks WindPulse is a full-stack web application designed for UK day-ahead wind power market analysis across January 2026 delivery decisions. Sourced exclusively from Elexon BMRS national-level wind actuals (`FUELHH`) and forecasts (`WINDFOR`), the platform provides two dedicated functions:
1. **Day-Ahead View:** Displays the latest national wind generation forecast published before the fixed decision cutoff on day $D-1$ evaluated against hourly aggregated actual generation for delivery day $D$.
2. **Accuracy View:** Evaluates quantitative forecast error metrics (MAE, RMSE, MBE, WAPE, and error distribution profiles) across the evaluation window.

Delivery-Day Range: Trading decisions made in January 2026 (Jan 1 to Jan 31) correspond to delivery days **2 Jan 2026 to 1 Feb 2026** (31 delivery days total), as confirmed by `GET /api/v1/dates`.

## Live App

The application is deployed and available at:
- **Primary:** [https://gridbricks.tanishportfolio.in/](https://gridbricks.tanishportfolio.in/)
- **Mirror:** [https://asdaf-delta.vercel.app](https://asdaf-delta.vercel.app)

Both live deployments connect to a managed Neon PostgreSQL database pre-loaded with the national wind dataset.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       Frontend: React 18 + Vite                             │
│           Tailwind CSS · Recharts Visualizations · State-based Tabs         │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ HTTP / REST
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                       Backend: Python 3.12 + FastAPI                        │
│          SQLAlchemy 2.0 · Psycopg 3 · Pydantic v2 · Pandas · NumPy          │
├─────────────────────────────────────────────────────────────────────────────┤
│  Active API Endpoints:                                                      │
│  - GET /health (alias: /api/health)       - GET /api/v1/metrics/hourly-prof.│
│  - GET / (alias: /api)                    - GET /api/v1/metrics/daily-time.│
│  - GET /api/v1/dates                      - GET /api/v1/metrics/distribution│
│  - GET /api/v1/day-ahead                  (aliases: /metrics/daily, /dist)  │
│  - GET /api/v1/metrics/summary                                              │
└──────────────────┬──────────────────────────────────────▲───────────────────┘
                   │ Pooled SSL Connection                │ Ingestion (Startup
┌──────────────────▼──────────────────┐                   │ AUTO_INGEST / Script)
│       Neon Serverless PostgreSQL    │                   │
│  - actual_wind: FUELHH actuals      │◄──────────────────┴───────────────────┐
│  - forecast_wind: WINDFOR forecasts │   Elexon BMRS API (FUELHH & WINDFOR)  │
└─────────────────────────────────────┘   Auto-loaded or ingest_data.py       │
                                          └───────────────────────────────────┘
```

### Technology Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend** | React 18, Vite | Single-page UI with state-based tab navigation (Day-Ahead and Accuracy) |
| **Styling & UI** | Tailwind CSS | Layout, responsive design, and component styling |
| **Visualizations** | Recharts | Day-ahead schedule area charts, error distribution histogram, diurnal profile |
| **Backend API** | Python 3.12, FastAPI | REST API endpoints, request validation, and OpenAPI documentation |
| **Database ORM** | SQLAlchemy 2.0, Psycopg 3 | PostgreSQL connection pooling and atomic query execution |
| **Analytics Engine** | Pandas, NumPy | Hourly resolution averaging, forecast alignment, and statistical error metrics |
| **Database** | Neon Serverless PostgreSQL | Cloud PostgreSQL storage with pooled SSL connections |
| **Containers** | Docker, Docker Compose | Container orchestration (FastAPI backend and Nginx frontend) |

### Active API Endpoints

- `GET /health` (alias: `/api/health`): Service health status and database row counts
- `GET /` (alias: `/api`): Root metadata endpoint
- `GET /api/v1/dates`: Returns available delivery dates (`2026-01-02` to `2026-02-01`) and decision dates (`2026-01-01` to `2026-01-31`)
- `GET /api/v1/day-ahead`: Hourly forecast vs. aggregated actual generation for a delivery date
- `GET /api/v1/metrics/summary`: Aggregate error metrics (MAE, RMSE, MBE, WAPE, quantiles)
- `GET /api/v1/metrics/hourly-profile`: 24-hour diurnal profile of average actuals, forecasts, and error
- `GET /api/v1/metrics/daily-timeline` (alias: `/api/v1/metrics/daily`): Day-by-day error metrics timeline
- `GET /api/v1/metrics/distribution` (alias: `/api/v1/metrics/dist`): Binned error frequency distribution

## Methodology

- **Resolution Matching:** Outturn actuals (`FUELHH`) are reported at half-hourly intervals ($48$ settlement periods per day). Because forecasts (`WINDFOR`) are issued at hourly resolution, consecutive half-hourly actuals within each hour are averaged arithmetically:
  $$\\text{Actual}_{\\text{hour } h} = \\frac{\\text{Actual}_{h:00} + \\text{Actual}_{h:30}}{2}$$
- **Decision Cutoff Assumption:** When making a procurement decision for delivery day $D$, trading decisions occur on day $D-1$ before a fixed cutoff configured in `backend/app/config.py` (`FIXED_DECISION_CUTOFF = "11:00"`, evaluated in UTC). For each delivery hour on day $D$, the system selects the latest forecast record satisfying:
  $$\\text{publishTime} \\le (D - 1)\\text{T}11:00:00\\text{Z}$$
  Any forecast published after 11:00 UTC on $D-1$ is strictly excluded to prevent look-ahead bias.
- **Delivery-Day Range:** Decisions made in January 2026 (Jan 1 to Jan 31) dictate delivery days from **2 Jan 2026 to 1 Feb 2026** ($31$ delivery days). Verified via `GET /api/v1/dates`, which returns delivery dates `2026-01-02` through `2026-02-01` and decision dates `2026-01-01` through `2026-01-31`. Underlying data is loaded across 31 Dec 2025 to 2 Feb 2026 to supply the necessary boundary decision gates.
- **Error Definition:** Forecast error is defined as forecast minus actual generation:
  $$e_i = F_i - A_i$$
  Positive values denote an over-forecast ($F > A$); negative values denote an under-forecast ($F < A$).
- **Accuracy Metrics:**
  - **Mean Absolute Error (MAE):** $\\text{MAE} = \\frac{1}{N}\\sum_{i=1}^N |F_i - A_i|$
  - **Root Mean Squared Error (RMSE):** $\\text{RMSE} = \\sqrt{\\frac{1}{N}\\sum_{i=1}^N (F_i - A_i)^2}$
  - **Mean Bias Error (MBE):** $\\text{MBE} = \\frac{1}{N}\\sum_{i=1}^N (F_i - A_i)$
  - **Weighted Absolute Percentage Error (WAPE):** $\\text{WAPE} = \\frac{\\sum_{i=1}^N |F_i - A_i|}{\\sum_{i=1}^N A_i} \\times 100\\%$

## Files and Directories

```
.
├── .dockerignore                       # Docker build context exclusions
├── .env.example                        # Template for environment configuration and Neon database URL
├── .gitignore                          # Git file exclusions (excludes .env, DEMO_SCRIPT.md, caches)
├── README.md                           # Project technical documentation and engineering reference
├── docker-compose.yml                  # Container orchestration for backend and frontend services
├── package.json                        # Root npm script shortcuts for container management and test runs
├── pytest.ini                          # Pytest configuration and pythonpath definitions
├── vercel.json                         # Vercel deployment specification and route rewrites
├── backend/
│   ├── Dockerfile                      # Python 3.12 container build definition for backend service
│   ├── pyproject.toml                  # Backend package metadata and Vercel framework definition
│   ├── requirements.txt                # Single source of truth for Python dependencies
│   ├── app/
│   │   ├── __init__.py                 # Application package marker
│   │   ├── config.py                   # Environment configuration, fixed 11:00 UTC cutoff, and dates
│   │   ├── database.py                 # SQLAlchemy engine and pooled session provider
│   │   ├── main.py                     # FastAPI application factory, lifespan handler, and root routes
│   │   ├── models.py                   # SQLAlchemy ORM models for actual_wind and forecast_wind
│   │   ├── schemas.py                  # Pydantic models for responses and summaries
│   │   ├── routers/
│   │   │   ├── __init__.py             # Routers package marker
│   │   │   ├── dates.py                # GET /api/v1/dates returning evaluation delivery and decision dates
│   │   │   ├── day_ahead.py            # GET /api/v1/day-ahead returning hourly forecast vs actual schedule
│   │   │   └── metrics.py              # GET /api/v1/metrics/* endpoints (summary, profile, timeline, dist)
│   │   └── services/
│   │       ├── __init__.py             # Services package marker
│   │       ├── analytics.py            # Resolution alignment, error metric calculations, and distribution
│   │       ├── data_store.py           # PostgreSQL data access layer with indexed queries and upserts
│   │       ├── elexon_client.py        # Async HTTP client streaming Elexon BMRS datasets
│   │       └── ingest_service.py       # Ingestion coordination with dataset completeness check
│   ├── scripts/
│   │   └── ingest_data.py              # Canonical ingestion script loading 31 Dec 2025 to 2 Feb 2026 data
│   └── tests/
│       ├── test_aggregation.py         # Unit tests verifying half-hourly to hourly actuals averaging logic
│       ├── test_alignment.py           # Unit tests verifying forecast exclusion after D-1 11:00 UTC cutoff
│       ├── test_api.py                 # Integration tests verifying status codes and schema shapes
│       ├── test_auto_ingest.py         # Unit tests verifying ingestion completeness check, skip, and error handling
│       └── test_metrics.py             # Unit tests verifying MAE, RMSE, MBE, WAPE, and edge cases
└── frontend/
    ├── Dockerfile                      # Multi-stage Node build and Nginx production server image
    ├── index.html                      # HTML document entrypoint
    ├── nginx.conf                      # Nginx reverse proxy configuration routing /api/ to backend
    ├── package-lock.json               # Locked frontend dependency versions
    ├── package.json                    # Frontend dependencies and Vite build scripts
    ├── postcss.config.js               # PostCSS configuration for Tailwind CSS processing
    ├── tailwind.config.js              # Tailwind CSS theme extensions and content paths
    ├── vite.config.js                  # Vite bundler configuration and local development proxy
    └── src/
        ├── App.jsx                     # Root application container with Day-Ahead and Accuracy views
        ├── index.css                   # Global Tailwind CSS styles and theme variables
        ├── main.jsx                    # React 18 application entry point
        ├── components/
        │   ├── AccuracyView.jsx        # Quantitative accuracy view (KPI cards, histogram, diurnal profile)
        │   ├── DayAheadView.jsx        # Day-ahead procurement view (hourly schedule chart, audit table)
        │   ├── Header.jsx              # Navigation header bar with branding and evaluation scope
        │   └── ui/
        │       ├── alert.jsx           # Notification alert box component
        │       ├── badge.jsx           # Status badge component
        │       ├── card.jsx            # Card container component
        │       ├── select.jsx          # Native select input component
        │       └── tabs.jsx            # Tabbed navigation primitives
        └── lib/
            └── utils.js                # Tailwind CSS class name merger utility
```

> **Note on Consolidated Config & Entrypoints:** Duplicate root configuration files (`requirements.txt`, `pyproject.toml`) and unused bridge files (`backend/main.py`, `backend/__init__.py`) were deleted. `backend/requirements.txt` is the single source of truth for dependencies used by both Docker (`backend/Dockerfile`) and Vercel (`services.backend.root = "backend"`).

## How to Start the Application

The deployed application connects to a pre-loaded Neon PostgreSQL database. To run locally from a fresh clone:

### 1. Prerequisites
- [Docker](https://docs.docker.com/get-docker/) and Docker Compose
- [Node.js](https://nodejs.org/) (optional, required if using root `npm run` shortcuts)
- [Python 3.12+](https://www.python.org/) (optional, required if running backend locally without Docker)

### 2. Configure Environment
Copy `.env.example` to `.env` and configure `DATABASE_URL` with your Neon PostgreSQL connection string:
```bash
cp .env.example .env
```
Ensure the connection string uses Neon's pooled endpoint with SSL required:
```env
DATABASE_URL=postgresql://user:password@ep-xxx-pooler.region.aws.neon.tech/neondb?sslmode=require
AUTO_INGEST=true
```

*DATABASE_URL Format:* `config.py` and `database.py` expect a standard Neon PostgreSQL URL (`postgresql://...`) with `?sslmode=require`. In `config.py`, `get_database_url()` automatically normalizes `postgres://` or `postgresql://` to `postgresql+psycopg://` to pair with SQLAlchemy 2.0 and the Psycopg 3 driver.

### 3. Data Ingestion & Seeding
Data can be loaded either automatically on startup or manually via the standalone script:

- **Automatic Ingestion (Default):** `AUTO_INGEST` defaults to `true` across all environments (and is forwarded into Docker via `docker-compose.yml`). On application startup, the backend runs a fast completeness check (`DataStore.get_data_status()`).
  - If the database is missing records or incomplete, it automatically streams 31 Dec 2025 to 2 Feb 2026 wind actuals and forecasts from Elexon BMRS.
  - If the database already contains complete data ($\ge 1500$ actuals, $\ge 10000$ forecasts), ingestion is bypassed immediately ($< 5\text{ms}$) with zero redundant API calls.
  - If Elexon BMRS is unreachable, a warning is logged and the server starts serving existing records without crashing.
- **Manual Ingestion Script:** You can also run the ingestion script directly at any time:
```bash
# Option A: Run inside backend container via Docker Compose
docker compose run --rm backend python backend/scripts/ingest_data.py

# Option B: Run locally
python backend/scripts/ingest_data.py
```

### 4. Start the Application
Start backend and frontend services using Docker Compose:
```bash
npm run server:start
# or: docker compose up -d
```

- **Frontend:** [http://localhost:3000](http://localhost:3000)
- **Backend API Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check:** [http://localhost:8000/health](http://localhost:8000/health)

To view live container logs:
```bash
npm run server:logs
```

To stop containers:
```bash
npm run server:stop
# or: docker compose down --remove-orphans
```

### 5. Run the Automated Test Suite
Run the test suite locally or inside the container:
```bash
pytest -v
# or via root npm script: npm test
```

Real test suite execution output:
```
backend/tests/test_aggregation.py::test_hourly_aggregation_two_half_hours PASSED [  5%]
backend/tests/test_aggregation.py::test_hourly_aggregation_single_half_hour PASSED [ 10%]
backend/tests/test_aggregation.py::test_hourly_aggregation_missing_data PASSED [ 15%]
backend/tests/test_alignment.py::test_forecast_alignment_selects_latest_before_cutoff PASSED [ 21%]
backend/tests/test_alignment.py::test_forecast_alignment_boundary_at_cutoff PASSED [ 26%]
backend/tests/test_alignment.py::test_forecast_alignment_strictly_excludes_future_forecasts PASSED [ 31%]
backend/tests/test_api.py::test_health_endpoint PASSED                   [ 36%]
backend/tests/test_api.py::test_dates_endpoint PASSED                    [ 42%]
backend/tests/test_day_ahead_endpoint PASSED                [ 47%]
backend/tests/test_metrics_summary_endpoint PASSED          [ 52%]
backend/tests/test_hourly_profile_endpoint PASSED           [ 57%]
backend/tests/test_distribution_endpoint PASSED             [ 63%]
backend/tests/test_dist_alias_endpoint PASSED               [ 68%]
backend/tests/test_daily_timeline_endpoint PASSED           [ 73%]
backend/tests/test_auto_ingest.py::test_ensure_data_ingested_skips_when_populated PASSED [ 78%]
backend/tests/test_auto_ingest.py::test_ensure_data_ingested_triggers_when_empty PASSED [ 84%]
backend/tests/test_auto_ingest.py::test_ensure_data_ingested_graceful_on_elexon_failure PASSED [ 89%]
backend/tests/test_metrics.py::test_accuracy_metrics_calculation PASSED  [ 94%]
backend/tests/test_metrics.py::test_zero_generation_and_empty_dataset PASSED [100%]

======================== 19 passed, 1 warning in 39.60s ========================
```

## Troubleshooting

- **DNS / Network Resolution Errors to Elexon BMRS (`data.elexon.co.uk`):**
  If `backend/scripts/ingest_data.py` raises socket resolution or connection errors when communicating with Elexon, check external network access. In Docker, ensure outbound connections are allowed; explicit DNS resolvers (`8.8.8.8`, `1.1.1.1`) are pre-configured in `docker-compose.yml`.
- **Neon PostgreSQL Connection / SSL Configuration:**
  SQLAlchemy requires PostgreSQL connections to Neon to specify `?sslmode=require`. Verify `DATABASE_URL` in `.env` is formatted as `postgresql://user:password@ep-...-pooler...neon.tech/neondb?sslmode=require`. Automatic reconnection for dropped pooled connections is handled via `pool_pre_ping=True` in `database.py`.

## AI Tools Disclosure

In accordance with assessment guidelines, AI assistance (Google Antigravity / Gemini) was used during development for:
- Researching Elexon BMRS API data structures and field specifications for `FUELHH` and `WINDFOR` streams.
- Scaffolding initial FastAPI route handlers, Pydantic schemas, and React components.
- Formulating test cases for edge conditions (zero generation, boundary timestamp matching, and missing data).
All implementation code, statistical calculations, and design decisions were reviewed and validated by the author.
