# GridBricks WindPulse

GridBricks WindPulse is a full-stack web application designed for UK day-ahead wind power market analysis across January 2026. The application performs two dedicated functions: (1) displaying the latest national wind generation forecast that was available when a day-ahead purchase decision had to be made, evaluated against outturn actual generation, and (2) evaluating forecast accuracy quantitatively using standard statistical error metrics and distribution profiles. Data is sourced strictly from Elexon BMRS national-level wind actuals (`FUELHH`) and forecasts (`WINDFOR`).

## Live App

The application is deployed and accessible at:
- Primary: [https://gridbricks.tanishportfolio.in/](https://gridbricks.tanishportfolio.in/)
- Mirror: [https://asdaf-delta.vercel.app](https://asdaf-delta.vercel.app)

The deployed instance connects to a pre-loaded Neon PostgreSQL database containing the complete January 2026 national wind dataset.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       Frontend: React 18 + Vite                             │
│             Tailwind CSS · Recharts Visualizations · Lucide Icons           │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ HTTP / REST
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                       Backend: Python 3.12 + FastAPI                        │
│          SQLAlchemy 2.0 · Psycopg 3 · Pydantic v2 · Pandas · NumPy          │
├─────────────────────────────────────────────────────────────────────────────┤
│  Endpoints:                                                                 │
│  - GET /api/v1/dates                      - GET /api/v1/metrics/daily       │
│  - GET /api/v1/day-ahead                  - GET /api/v1/metrics/dist        │
│  - GET /api/v1/metrics/summary            - GET /health                     │
│  - GET /api/v1/metrics/hourly-profile                                       │
└──────────────────┬──────────────────────────────────────┬───────────────────┘
                   │ Pooled Connection (SSL)              │ Ingestion Script Only
┌──────────────────▼──────────────────┐   ┌───────────────▼───────────────────┐
│       Neon Serverless PostgreSQL    │   │         Elexon BMRS API           │
│  - actual_wind: FUELHH actuals      │   │  - FUELHH (30-min actual wind)    │
│  - forecast_wind: WINDFOR forecasts │   │  - WINDFOR (hourly wind forecasts)│
└─────────────────────────────────────┘   │  Loaded once via ingest_data.py   │
                                          └───────────────────────────────────┘
```

### Technology Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend** | React 18, Vite | Single-page UI and client-side routing |
| **Styling & UI** | Tailwind CSS | Utility-first layout and responsive styling |
| **Charts** | Recharts | Day-ahead generation areas, error distribution histogram, diurnal profile |
| **Backend API** | Python 3.12, FastAPI | REST API endpoints and request validation |
| **Database ORM** | SQLAlchemy 2.0, Psycopg 3 | PostgreSQL connection pooling and atomic query execution |
| **Analytics** | Pandas, NumPy | Hourly resolution averaging, forecast alignment, and statistical error metrics |
| **Database** | Neon Serverless PostgreSQL | Managed cloud PostgreSQL storage with pooled SSL connections |
| **Containers** | Docker, Docker Compose | Multi-container orchestration (backend and frontend reverse proxy) |

## Methodology

- **Resolution Matching:** Outturn wind actuals (`FUELHH`) are reported at half-hourly resolution ($48$ settlement periods per day). Because forecasts (`WINDFOR`) are issued at hourly resolution, consecutive half-hourly actuals within each hour are averaged arithmetically:
  $$\text{Actual}_{\text{hour } h} = \frac{\text{Actual}_{h:00} + \text{Actual}_{h:30}}{2}$$
- **Decision Cutoff Assumption:** When making a procurement decision for delivery day $D$, trading decisions are assumed to occur on day $D-1$ before a fixed cutoff time configured in `backend/app/config.py` (`FIXED_DECISION_CUTOFF = "11:00"`, evaluated in UTC). For each delivery hour on day $D$, the system selects the latest forecast record whose publication timestamp satisfies:
  $$\text{publishTime} \le (D - 1)\text{T}11:00:00\text{Z}$$
  Any forecast published after 11:00 UTC on $D-1$ is strictly excluded to prevent look-ahead bias.
- **Error Definition:** Forecast error is defined as forecast minus actual generation:
  $$e_i = F_i - A_i$$
  Positive values ($e_i > 0$) denote an over-forecast; negative values ($e_i < 0$) denote an under-forecast.
- **Accuracy Metrics:**
  - **Mean Absolute Error (MAE):** $\text{MAE} = \frac{1}{N}\sum_{i=1}^N |F_i - A_i|$
  - **Root Mean Squared Error (RMSE):** $\text{RMSE} = \sqrt{\frac{1}{N}\sum_{i=1}^N (F_i - A_i)^2}$
  - **Mean Bias Error (MBE):** $\text{MBE} = \frac{1}{N}\sum_{i=1}^N (F_i - A_i)$
  - **Weighted Absolute Percentage Error (WAPE):** $\text{WAPE} = \frac{\sum_{i=1}^N |F_i - A_i|}{\sum_{i=1}^N A_i} \times 100\%$

## Files and Directories

```
Gridbricks/
├── .dockerignore                       # Docker build context exclusions
├── .env.example                        # Template for database connection string and environment variables
├── .gitignore                          # Git file exclusion rules (excludes credentials and private files)
├── docker-compose.yml                  # Multi-container orchestration for backend and frontend services
├── package.json                        # Root npm script shortcuts for container management and test runs
├── pyproject.toml                      # Root Python packaging and tool configuration
├── pytest.ini                          # Pytest configuration and pythonpath definition
├── README.md                           # Project engineering documentation and setup guide
├── requirements.txt                    # Root Python dependencies list
├── vercel.json                         # Vercel deployment specification and API route rewrites
├── backend/
│   ├── app/
│   │   ├── __init__.py                 # Backend application package marker
│   │   ├── config.py                   # Environment variable loader and fixed 11:00 UTC decision cutoff constant
│   │   ├── database.py                 # SQLAlchemy engine configuration and pooled session provider
│   │   ├── main.py                     # FastAPI application factory, lifespan handler, CORS, and root routes
│   │   ├── models.py                   # SQLAlchemy ORM models for actual_wind and forecast_wind
│   │   ├── schemas.py                  # Pydantic response models for schedules, metrics, and profiles
│   │   ├── routers/
│   │   │   ├── __init__.py             # Routers package marker
│   │   │   ├── dates.py                # GET /api/v1/dates returning available delivery and decision dates
│   │   │   ├── day_ahead.py            # GET /api/v1/day-ahead returning hourly forecast vs actual generation
│   │   │   └── metrics.py              # GET /api/v1/metrics/* endpoints (summary, hourly profile, daily, dist)
│   │   └── services/
│   │       ├── __init__.py             # Services package marker
│   │       ├── analytics.py            # Resolution alignment, error metric calculations, and distribution binner
│   │       ├── data_store.py           # PostgreSQL data access layer with DISTINCT ON queries and upsert operations
│   │       └── elexon_client.py        # Async HTTP client used by ingestion script to stream BMRS datasets
│   ├── scripts/
│   │   └── ingest_data.py              # One-time data ingestion script loading Elexon data for Dec 31 2025 - Feb 2 2026
│   ├── tests/
│   │   ├── __init__.py                 # Test package marker
│   │   ├── test_aggregation.py         # Unit tests verifying half-hourly to hourly actuals averaging logic
│   │   ├── test_alignment.py           # Unit tests verifying strict exclusion of forecasts after D-1 11:00 UTC cutoff
│   │   ├── test_api.py                 # Integration tests verifying status codes and schema shapes across remaining endpoints
│   │   └── test_metrics.py             # Unit tests verifying MAE, RMSE, MBE, WAPE, and quantile calculations
│   ├── Dockerfile                      # Python 3.12 container build definition for backend service
│   ├── pyproject.toml                  # Backend package configuration
│   └── requirements.txt                # Backend Python package requirements
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── ui/
    │   │   │   ├── alert.jsx           # Alert notification box component
    │   │   │   ├── badge.jsx           # Badge label component
    │   │   │   ├── card.jsx            # Card container component
    │   │   │   ├── select.jsx          # Native select wrapper component
    │   │   │   └── tabs.jsx            # Tabbed interface navigation primitives
    │   │   ├── AccuracyView.jsx        # Quantitative accuracy view (KPI cards, histogram, diurnal, daily timeline)
    │   │   ├── DayAheadView.jsx        # Day-ahead procurement view (hourly schedule chart, KPI summary, audit table)
    │   │   └── Header.jsx              # Application header bar with brand title and subtitle
    │   ├── lib/
    │   │   └── utils.js                # Tailwind class name merge utility
    │   ├── App.jsx                     # Root application container with two core tabs (Day-Ahead and Accuracy)
    │   ├── index.css                   # Global Tailwind CSS directives and theme variables
    │   └── main.jsx                    # React 18 application entry point
    ├── Dockerfile                      # Multi-stage Node build and Nginx production image definition
    ├── index.html                      # HTML document template
    ├── nginx.conf                      # Nginx reverse proxy configuration routing /api/ requests to backend
    ├── package.json                    # Frontend dependencies and Vite build scripts
    ├── package-lock.json               # Locked frontend dependency versions
    ├── postcss.config.js               # PostCSS configuration for Tailwind CSS processing
    ├── tailwind.config.js              # Tailwind CSS theme extension and content path configuration
    └── vite.config.js                  # Vite bundler configuration and local development proxy
```

## How to Start the Application

The deployed application already reads from a pre-loaded Neon PostgreSQL database. To run locally from a fresh clone:

### 1. Prerequisites
- [Docker](https://docs.docker.com/get-docker/) & Docker Compose
- [Node.js](https://nodejs.org/) (optional, required if using root `npm run` shortcuts)

### 2. Configure Environment
Copy `.env.example` to `.env` and set `DATABASE_URL` to your Neon PostgreSQL connection string:
```bash
cp .env.example .env
```
Ensure the connection string uses Neon's pooled endpoint with SSL required:
```env
DATABASE_URL=postgresql://user:password@ep-xxx-pooler.region.aws.neon.tech/neondb?sslmode=require
```

### 3. Load Data Once (Ingestion Script)
Run `backend/scripts/ingest_data.py` once to populate the Neon database with national wind actuals (`FUELHH`) and forecasts (`WINDFOR`) for the evaluation window (December 31, 2025 through February 2, 2026):

```bash
# Option A: Run inside backend container via Docker Compose
docker compose run --rm backend python backend/scripts/ingest_data.py

# Option B: Run locally (with Python 3.12+ and dependencies installed)
python backend/scripts/ingest_data.py
```

### 4. Start the Application
Start both backend and frontend containers:
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
# or: docker compose logs -f
```

To stop containers:
```bash
npm run server:stop
# or: docker compose down --remove-orphans
```

### 5. Run the Automated Test Suite
Run the test suite inside the backend container or locally:
```bash
npm test
# or: docker compose exec backend pytest -v
# or locally: pytest -v
```

Real test suite execution output:
```
backend/tests/test_aggregation.py::test_hourly_aggregation_two_half_hours PASSED
backend/tests/test_aggregation.py::test_hourly_aggregation_single_half_hour PASSED
backend/tests/test_aggregation.py::test_hourly_aggregation_missing_data PASSED
backend/tests/test_alignment.py::test_forecast_alignment_selects_latest_before_cutoff PASSED
backend/tests/test_alignment.py::test_forecast_alignment_boundary_at_cutoff PASSED
backend/tests/test_alignment.py::test_forecast_alignment_strictly_excludes_future_forecasts PASSED
backend/tests/test_api.py::test_health_endpoint PASSED
backend/tests/test_dates_endpoint PASSED
backend/tests/test_day_ahead_endpoint PASSED
backend/tests/test_metrics_summary_endpoint PASSED
backend/tests/test_hourly_profile_endpoint PASSED
backend/tests/test_distribution_endpoint PASSED
backend/tests/test_dist_alias_endpoint PASSED
backend/tests/test_daily_timeline_endpoint PASSED
backend/tests/test_metrics.py::test_accuracy_metrics_calculation PASSED
backend/tests/test_metrics.py::test_zero_generation_and_empty_dataset PASSED

======================== 16 passed, 1 warning in 40.01s ========================
```

## Troubleshooting

- **DNS / Network Errors During Data Ingestion (`data.elexon.co.uk`):**
  If `backend/scripts/ingest_data.py` raises a socket resolution error (`[Errno -5] No address associated with hostname` or connection timeout) when reaching Elexon BMRS, verify external internet access and DNS resolution. In Docker environments, ensure the host network allows outbound connections or that explicit DNS resolvers (`8.8.8.8`, `1.1.1.1`) configured in `docker-compose.yml` are reachable.
- **Neon Database Connection / SSL Errors:**
  FastAPI and SQLAlchemy require PostgreSQL connections to include `?sslmode=require` when communicating with Neon serverless endpoints. Verify that `DATABASE_URL` in `.env` is formatted as `postgresql+psycopg://user:password@ep-...-pooler...neon.tech/neondb?sslmode=require`. If pooled connections time out after idle periods, `pool_pre_ping=True` configured in `database.py` automatically reconnects dropped connections.

## AI Tools Disclosure

In accordance with assessment guidelines, AI assistance (Google Antigravity / Gemini) was used during development for:
- Researching Elexon BMRS API data structures and field specifications for `FUELHH` and `WINDFOR` streams.
- Scaffolding initial FastAPI route handlers, Pydantic schemas, and React components.
- Formulating test cases for edge conditions (zero generation, boundary timestamp matching, and missing data).
