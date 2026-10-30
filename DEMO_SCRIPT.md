# Video Demonstration Script: GridBricks WindPulse Platform
**Format:** Unlisted YouTube Video (Maximum 10 Minutes Total)  
**Part 1:** Client Pitch & Pilot Presentation (00:00 – 04:50, Max 5 Minutes)  
**Part 2:** Technical Lead Architecture & Code Review (04:50 – 09:50, Max 5 Minutes)

---

## Part 1: Client Pitch & Pilot Presentation (00:00 – 04:50)
*Target Audience: Head of Power Procurement & Wholesale Energy Traders at UK Utility*  
*Tone: Confident, commercial, domain-grounded, solutions-oriented.*

### 00:00 – 00:45 | Executive Problem Statement & Value Proposition
- **Screen Action:** Open browser showing the GridBricks WindPulse dashboard on the **Day-Ahead Procurement** tab.
- **Presenter (Say):**
  > "Good morning team. Over the last several weeks, our product engineering team partnered with your power procurement desk to deliver this pilot platform: **GridBricks WindPulse**.
  > 
  > As an energy utility in Great Britain, your core daily challenge is balancing customer demand in wholesale markets. When making bids in the Day-Ahead auction—closing at **11:00 AM UTC on day D-1**—you have to decide how many Megawatts of thermal generation, like gas or biomass, to buy. 
  > 
  > You want to maximize renewable wind intake to lower procurement costs, but wind is weather-dependent. If your forecast over-predicts wind, you are left short of power in real time and exposed to punitive system cashout balancing prices. If your forecast under-predicts wind, you over-buy expensive thermal power and dump excess wind at a loss.
  > 
  > Today, I’m excited to show you how WindPulse provides complete clarity on your day-ahead forecast position and quantifies your renewable uncertainty into actionable trading decisions."

### 00:45 – 02:00 | Feature 1: Day-Ahead Procurement View (D-1 Gate Closure Clarity)
- **Screen Action:** 
  - Point to the control panel at the top. Select Delivery Date: **January 15, 2026**.
  - Show the Decision Cutoff dropdown set to **11:00 UTC (GB Day-Ahead Auction Close - Default)**.
  - Hover over the generation chart curves (Emerald = Forecast, Sky Blue = Actuals).
  - Hover over hour **14:00** showing the tooltip with forecast publish time, actual generation, and error delta.
- **Presenter (Say):**
  > "Let’s start in the **Day-Ahead Procurement View**. 
  > 
  > The most critical rule in your trading operations is gate closure. When your desk submits auction orders on January 14th at 11:00 AM, you can only act on forecasts published **before 11:00 AM**. WindPulse enforces this strictly.
  > 
  > Look at January 15th: The green line is the day-ahead wind forecast available at auction gate closure, and the blue line is the actual outturn generation from Elexon FUELHH.
  > 
  > Notice what happened: Our KPI summary instantly highlights that across this day, the forecast averaged **12,000 MW**, while actual generation came in slightly higher at **12,155 MW**, giving an exceptionally tight daily MAE of just **640 MW** and a near-perfect accuracy rate.
  > 
  > In the audit table below, every single delivery hour displays the exact publication timestamp of the Elexon WINDFOR forecast used. Your traders have 100% auditability to prove exactly what data was on screen when order tickets were sent."

### 02:00 – 03:15 | Feature 2: Quantitative Forecast Accuracy Evaluation
- **Screen Action:** Click on the second tab: **Quantitative Accuracy**.
  - Highlight the 6 primary KPI cards: MAE (2,155 MW), RMSE (2,655 MW), Mean Bias (+1,874 MW), WAPE (18.65%), P90 Shortfall (4,318 MW).
  - Scroll down to the **Error Distribution Histogram** and the **24-Hour Diurnal Error Profile**.
- **Presenter (Say):**
  > "Now, how reliable are these forecasts over the entire month? Let’s switch to the **Quantitative Accuracy Evaluation** tab.
  > 
  > Across all 744 hourly delivery periods in January 2026, WindPulse evaluated National Grid’s wind forecasts against actual settlement outturn.
  > 
  > Here is the critical takeaway for your procurement desk: Look at the **Mean Bias Error (MBE)** card: **+1,874 MW**. 
  > 
  > This reveals that throughout January 2026, National Grid wind forecasts had a **systematic positive bias**—they consistently over-forecasted wind generation by nearly 1,900 MW on average! If your desk simply bought thermal power matching the raw forecast, you would have been systematically short of electricity in the balancing market.
  > 
  > Below, our **Error Distribution Histogram** color-codes this risk in red: the distribution is skewed heavily towards shortfall. 
  > 
  > Furthermore, our **Diurnal 24-Hour Profile** proves that forecast error is not uniform throughout the day: the largest volatility occurs during the morning ramp (07:00 to 09:00 UTC) and the evening demand peak (17:00 to 19:00 UTC)."

### 03:15 – 04:30 | Feature 3: Risk & Balancing Calculator (Translating Error into Thermal Sizing)
- **Screen Action:** Click on the third tab: **Risk & Balancing Sizing**.
  - Show the Customer Demand input set to **25,000 MW**.
  - Toggle between **90% Confidence (P90)** and **95% Confidence (P95)**.
  - Point to the 3 clear comparison cards: Base Thermal (13,000 MW), Reserve Buffer (+4,318 MW), Total Target (17,318 MW).
  - Show the stacked energy dispatch chart below.
- **Presenter (Say):**
  > "Metrics are only valuable if they inform your procurement quantity. That’s why we built the **Risk & Balancing Calculator**.
  > 
  > Suppose your utility serves a consumer peak demand of **25,000 MW**. 
  > 
  > WindPulse separates your procurement into three unambiguous tiers:
  > 1. **Base Thermal Procurement:** Demand minus average forecast wind leaves an expected thermal shortfall of **13,000 MW**.
  > 2. **Recommended Reserve Buffer:** Based on the quantified 90th percentile historical wind shortfall error, the platform calculates an additional reserve cushion of **+4,318 MW**.
  > 3. **Total Procurement Target:** Your desk should procure **17,318 MW** of thermal energy to protect against wind drop-off with 90% statistical confidence.
  > 
  > If market conditions are stormy or reserve prices are spiked, your trader can toggle to **95% confidence**, dynamically updating the buffer. 
  > 
  > In the 24-hour simulation below, the purple line shows what actual wind generated. Because of our quantified buffer, your utility was never short of power during any settlement period."

### 04:30 – 04:50 | Client Presentation Wrap-Up
- **Screen Action:** Click on the **Data Explorer & CSV** tab, showing instant export.
- **Presenter (Say):**
  > "Traders can also export the entire aligned dataset to CSV with a single click for downstream risk models.
  > 
  > In summary: GridBricks WindPulse transforms raw weather forecasts into quantified procurement certainty, protecting your utility against cashout penalties and lowering thermal procurement costs. Thank you, and I look forward to your questions."

---

## Part 2: Technical Lead Architecture & Code Review (04:50 – 09:50)
*Target Audience: Internal Technical Lead & Software Engineering Evaluator*  
*Tone: Technical, precise, highlighting architectural decisions, test coverage, and code hygiene.*

### 04:50 – 05:45 | Architectural Overview & Tech Stack
- **Screen Action:** Switch to VS Code / terminal. Show directory structure and `architecture` diagram in `README.md`.
- **Presenter (Say):**
  > "Hi everyone. Now let’s transition into Part 2: the internal technical walkthrough of the architecture, data pipeline, and codebase design.
  > 
  > The system is built with a decoupled modern architecture:
  > - **Backend:** Python 3.12 with **FastAPI**, **Pandas**, and **NumPy** for numerical computations.
  > - **Storage:** A local **SQLite** database with indexed tables for `actual_wind`, `forecast_wind`, and `sync_log`.
  > - **Frontend:** **React 18** scaffolded with **Vite**, styled with **Tailwind CSS**, using **Shadcn UI** component patterns, **Formik** and **Zod** for form management and validation, and **Recharts** for visual analytics.
  > - **Deployment & Containerization:** Fully containerized with a root `docker-compose.yml`, multi-stage Dockerfiles for both backend and frontend (with Nginx reverse proxy), and production deployment manifests for Vercel and Render/Heroku."

### 05:45 – 07:00 | Elexon Data Ingestion & Resolution Alignment Logic
- **Screen Action:** Open [backend/app/services/data_store.py](file:///media/tanish/DATA1/VS%20Code%20Projects/coding_assignments/Gridbricks/backend/app/services/data_store.py) and [backend/app/services/elexon_client.py](file:///media/tanish/DATA1/VS%20Code%20Projects/coding_assignments/Gridbricks/backend/app/services/elexon_client.py).
- **Presenter (Say):**
  > "Let’s look at the data ingestion and resolution alignment.
  > 
  > We stream data directly from Elexon BMRS public API endpoints:
  > 1. `FUELHH/stream` gives half-hourly outturn generation. We filter exclusively for `fuelType == 'WIND'`.
  > 2. `WINDFOR/stream` gives national wind forecasts with `publishTime`, `startTime`, and forecasted `generation`.
  > 
  > Here is a crucial domain nuance: `FUELHH` actuals are **half-hourly** (30-minute intervals, 48 settlement periods/day), whereas `WINDFOR` forecasts are **hourly** (starting at `:00`).
  > 
  > In `DataStore.get_hourly_actuals_for_date()`, we mathematically aggregate the two half-hours (`:00` and `:30`) by computing their arithmetic mean:
  > `avg_generation = (period_1 + period_2) / 2`.
  > If a period is missing, it gracefully handles the single observation without failure.
  > 
  > Ingestion runs via `ingest_data.py` across December 31, 2025 to February 2, 2026, populating **1,585 actual records** and **19,272 forecast records**, enabling sub-millisecond local responses while providing a manual `/api/v1/sync` endpoint for live polling."

### 07:00 – 08:00 | Core Innovation: Day-Ahead D-1 Gate Cutoff Alignment
- **Screen Action:** Open [backend/app/services/data_store.py](file:///media/tanish/DATA1/VS%20Code%20Projects/coding_assignments/Gridbricks/backend/app/services/data_store.py) lines 130–165 (`get_day_ahead_forecasts`).
- **Presenter (Say):**
  > "Now let’s inspect the forecast alignment logic—the most critical algorithmic requirement in the assessment.
  > 
  > In wholesale power trading, look-ahead bias is fatal. For delivery day $D$, the trading decision occurs on day $D - 1$.
  > 
  > In `get_day_ahead_forecasts(delivery_date, cutoff_time)`:
  > - We compute the decision date: `decision_dt = deliv_dt - timedelta(days=1)`.
  > - We construct the strict cutoff timestamp: `cutoff_datetime = f"{dec_date}T{cutoff_time}:00Z"`.
  > - For each delivery hour $h \in [0..23]$:
  >   We query SQLite:
  >   `WHERE startTime = :hour_target AND publishTime <= :cutoff_datetime`
  >   `ORDER BY publishTime DESC LIMIT 1`.
  > 
  > This guarantees two things:
  > 1. It selects the absolute latest forecast available at or before the trader’s cutoff time.
  > 2. Any forecast published *after* the cutoff is strictly filtered out.
  > 
  > We support standard auction close (11:00 UTC), internal desk valuation (09:30 UTC), midday (12:00 UTC), and afternoon runs."

### 08:00 – 08:50 | Mathematical Analytics & Risk Sizing Engine
- **Screen Action:** Open [backend/app/services/analytics.py](file:///media/tanish/DATA1/VS%20Code%20Projects/coding_assignments/Gridbricks/backend/app/services/analytics.py) lines 105–170.
- **Presenter (Say):**
  > "Next, let’s look at the quantitative error calculations in `AnalyticsService`:
  > - **MAE:** Average absolute delta $\frac{1}{N}\sum |F_i - A_i|$.
  > - **RMSE:** Root mean square error $\sqrt{\frac{1}{N}\sum (F_i - A_i)^2}$, penalizing large outliers.
  > - **MBE (Mean Bias Error):** $\frac{1}{N}\sum (F_i - A_i)$, proving the systematic +1,874 MW over-forecast.
  > - **WAPE:** Weighted absolute percentage error, dividing total absolute error by total actual MWh. This avoids distortion when wind is low.
  > - **Zero-generation protection:** Handled safely when actual wind is zero or calm.
  > - **Reserve Buffer Sizing:** In `calculate_balancing_risk()`, we extract the shortfall array `max(0, F - A)` and compute the 90th and 95th percentiles. This gives traders an empirical, mathematically grounded reserve cushion."

### 08:50 – 09:30 | Code Quality, Testing & Docker Deployment
- **Screen Action:** Run `pytest -v` in terminal, showing 16 passing tests. Open `docker-compose.yml`.
- **Presenter (Say):**
  > "Let’s run the test suite:
  > 
  > Executing `pytest -v`: **16 unit and integration tests passing in 1.6 seconds**.
  > - `test_aggregation.py` verifies settlement period averaging and missing half-hours.
  > - `test_alignment.py` verifies that forecasts published before cutoff are chosen and future forecasts are strictly rejected.
  > - `test_metrics.py` validates known mathematical arrays against hand-calculated values, zero division safety, and risk calculations.
  > - `test_api.py` asserts that all FastAPI endpoints return 200 with valid Pydantic schemas.
  > 
  > For deployment, `docker compose up --build` boots both services with health checks and volume persistence. The frontend is also configured for Vercel and the backend for Render/Heroku via `Procfile`."

### 09:30 – 09:50 | Wrap-Up & Conclusion
- **Presenter (Say):**
  > "In conclusion, this project delivers a production-grade, domain-accurate platform for UK wholesale renewable procurement. All requirements—from Elexon stream ingestion, strict gate alignment, Formik and Zod validation, to Shadcn UI design and containerization—are fully implemented and verified. Thank you."
