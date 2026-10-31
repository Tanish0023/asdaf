import { useState, useEffect } from "react"
import {
  BarChart, Bar, LineChart, Line, ComposedChart, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer, Legend, Cell, ReferenceLine
} from "recharts"
import {
  BarChart3, TrendingUp, AlertCircle, Calendar,
  Gauge, Target, Activity, Clock
} from "lucide-react"

import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "./ui/card"
import { Select } from "./ui/select"
import { Alert, AlertTitle, AlertDescription } from "./ui/alert"

export function AccuracyView({ availableDates }) {
  const [loading, setLoading] = useState(false)
  const [startDate, setStartDate] = useState("2026-01-02")
  const [endDate, setEndDate] = useState("2026-02-01")
  const [metrics, setMetrics] = useState(null)
  const [hourlyProfile, setHourlyProfile] = useState([])
  const [dailyTimeline, setDailyTimeline] = useState([])
  const [distribution, setDistribution] = useState(null)
  const [error, setError] = useState(null)

  const fetchAllMetrics = async (start, end) => {
    setLoading(true)
    setError(null)
    try {
      const q = `start_date=${start}&end_date=${end}`
      const [resSummary, resProfile, resTimeline, resDist] = await Promise.all([
        fetch(`/api/v1/metrics/summary?${q}`),
        fetch(`/api/v1/metrics/hourly-profile?${q}`),
        fetch(`/api/v1/metrics/daily-timeline?${q}`),
        fetch(`/api/v1/metrics/distribution?${q}`),
      ])

      if (!resSummary.ok || !resProfile.ok || !resTimeline.ok || !resDist.ok) {
        throw new Error("One or more metrics queries failed")
      }

      const summaryData = await resSummary.json()
      const profileData = await resProfile.json()
      const timelineData = await resTimeline.json()
      const distData = await resDist.json()

      setMetrics(summaryData)
      setHourlyProfile(profileData.profiles || [])
      setDailyTimeline(timelineData.timeline || [])
      setDistribution(distData)
    } catch (err) {
      setError(err.message || "Failed to load accuracy metrics")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAllMetrics(startDate, endDate)
  }, [startDate, endDate])

  useEffect(() => {
    if (availableDates?.delivery_dates?.length) {
      if (!startDate) setStartDate(availableDates.delivery_dates[0])
      if (!endDate) setEndDate(availableDates.delivery_dates[availableDates.delivery_dates.length - 1])
    }
  }, [availableDates])

  // Custom Histogram Tooltip
  const DistTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const d = payload[0].payload
      return (
        <div className="bg-slate-900 border border-slate-700 p-2.5 rounded-lg text-xs shadow-xl font-mono">
          <div className="font-semibold text-white mb-1">Error Range: {d.bin_label} MW</div>
          <div className="text-slate-300">Observation Count: <strong className="text-white">{d.count}</strong> hours</div>
          <div className="text-slate-300">Share: <strong className="text-emerald-400">{d.percentage}%</strong></div>
        </div>
      )
    }
    return null
  }

  const dateOptions = availableDates?.delivery_dates || [
    ...Array.from({ length: 30 }, (_, i) => {
      const day = String(i + 2).padStart(2, "0")
      return `2026-01-${day}`
    }),
    "2026-02-01"
  ]

  return (
    <div className="space-y-6">
      {/* Filter Control */}
      <Card className="bg-slate-900/60 border-slate-800">
        <CardContent className="p-4 sm:p-5">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div className="flex flex-wrap items-center gap-4">
              <div className="min-w-[160px] space-y-1.5">
                <label htmlFor="startDate" className="text-xs font-medium text-slate-300 flex items-center gap-1.5">
                  <Calendar className="h-3.5 w-3.5 text-emerald-400" />
                  Start Date
                </label>
                <Select
                  id="startDate"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                >
                  {dateOptions.map((d) => (
                    <option key={d} value={d} className="bg-slate-900 text-white">
                      {d}
                    </option>
                  ))}
                </Select>
              </div>

              <div className="min-w-[160px] space-y-1.5">
                <label htmlFor="endDate" className="text-xs font-medium text-slate-300 flex items-center gap-1.5">
                  <Calendar className="h-3.5 w-3.5 text-emerald-400" />
                  End Date
                </label>
                <Select
                  id="endDate"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                >
                  {dateOptions.map((d) => (
                    <option key={d} value={d} className="bg-slate-900 text-white">
                      {d}
                    </option>
                  ))}
                </Select>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <div className="flex items-center text-xs text-slate-300 bg-slate-950/80 px-4 py-2.5 rounded-lg border border-slate-800">
                <Clock className="h-4 w-4 text-emerald-400 mr-2 shrink-0" />
                <span>Decision Cutoff: <strong className="text-emerald-400">11:00 UTC</strong> on D-1</span>
              </div>
              <div className="hidden xl:flex items-center text-xs text-slate-400 bg-slate-950/60 px-4 py-2.5 rounded-lg border border-slate-800">
                <span>
                  Evaluating <strong className="text-emerald-400">{metrics?.total_observations || 0}</strong> hourly delivery intervals
                </span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Error Loading Metrics</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Primary KPI Metrics Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 sm:gap-4">
        {/* MAE */}
        <Card className="bg-slate-900/80 border-slate-800 p-4 relative overflow-hidden">
          <div className="text-[11px] text-slate-400 font-medium">Mean Absolute Error</div>
          <div className="text-2xl font-bold font-mono text-emerald-400 mt-1">
            {metrics?.mae?.toLocaleString() ?? "—"}{" "}
            <span className="text-xs font-normal text-slate-400">MW</span>
          </div>
          <div className="text-[10px] text-slate-500 mt-1">
            Avg magnitude of forecast error
          </div>
          <div className="absolute top-2 right-2 text-slate-800">
            <Target className="h-8 w-8 stroke-1" />
          </div>
        </Card>

        {/* RMSE */}
        <Card className="bg-slate-900/80 border-slate-800 p-4 relative overflow-hidden">
          <div className="text-[11px] text-slate-400 font-medium">Root Mean Sq Error</div>
          <div className="text-2xl font-bold font-mono text-teal-400 mt-1">
            {metrics?.rmse?.toLocaleString() ?? "—"}{" "}
            <span className="text-xs font-normal text-slate-400">MW</span>
          </div>
          <div className="text-[10px] text-slate-500 mt-1">
            Penalizes large outlier misses
          </div>
          <div className="absolute top-2 right-2 text-slate-800">
            <Activity className="h-8 w-8 stroke-1" />
          </div>
        </Card>

        {/* Mean Bias (MBE) */}
        <Card className="bg-slate-900/80 border-slate-800 p-4 relative overflow-hidden">
          <div className="text-[11px] text-slate-400 font-medium">Mean Bias Error (MBE)</div>
          <div className={`text-2xl font-bold font-mono mt-1 ${metrics?.mbe > 0 ? "text-rose-400" : "text-sky-400"}`}>
            {metrics?.mbe ? `${metrics.mbe > 0 ? "+" : ""}${metrics.mbe.toLocaleString()}` : "—"}{" "}
            <span className="text-xs font-normal text-slate-400">MW</span>
          </div>
          <div className="text-[10px] text-slate-500 mt-1">
            {metrics?.mbe > 0 ? "Systematic over-forecast" : "Systematic under-forecast"}
          </div>
          <div className="absolute top-2 right-2 text-slate-800">
            <TrendingUp className="h-8 w-8 stroke-1" />
          </div>
        </Card>

        {/* WAPE */}
        <Card className="bg-slate-900/80 border-slate-800 p-4 relative overflow-hidden">
          <div className="text-[11px] text-slate-400 font-medium">Weighted Absolute % Error</div>
          <div className="text-2xl font-bold font-mono text-amber-400 mt-1">
            {metrics?.wape ?? "—"}%
          </div>
          <div className="text-[10px] text-slate-500 mt-1">
            Accuracy: <strong className="text-emerald-400">{metrics?.accuracy_rate}%</strong>
          </div>
          <div className="absolute top-2 right-2 text-slate-800">
            <Gauge className="h-8 w-8 stroke-1" />
          </div>
        </Card>

        {/* P90 Error Quantile */}
        <Card className="bg-slate-900/80 border-slate-800 p-4 relative overflow-hidden">
          <div className="text-[11px] text-slate-400 font-medium">P90 Error Quantile</div>
          <div className="text-2xl font-bold font-mono text-rose-400 mt-1">
            {metrics?.p90_error ? `${metrics.p90_error > 0 ? "+" : ""}${metrics.p90_error.toLocaleString()}` : "—"}{" "}
            <span className="text-xs font-normal text-slate-400">MW</span>
          </div>
          <div className="text-[10px] text-slate-500 mt-1">
            90th percentile error (F - A)
          </div>
        </Card>

        {/* P95 Error Quantile */}
        <Card className="bg-slate-900/80 border-slate-800 p-4 relative overflow-hidden">
          <div className="text-[11px] text-slate-400 font-medium">P95 Error Quantile</div>
          <div className="text-2xl font-bold font-mono text-orange-400 mt-1">
            {metrics?.p95_error ? `${metrics.p95_error > 0 ? "+" : ""}${metrics.p95_error.toLocaleString()}` : "—"}{" "}
            <span className="text-xs font-normal text-slate-400">MW</span>
          </div>
          <div className="text-[10px] text-slate-500 mt-1">
            95th percentile error (F - A)
          </div>
        </Card>
      </div>

      {/* Quantiles & Extremes Secondary Bar */}
      <Card className="bg-slate-900/50 border-slate-800">
        <CardContent className="p-4 grid grid-cols-2 md:grid-cols-4 gap-4 text-xs font-mono">
          <div className="flex justify-between items-center p-2 rounded-lg bg-slate-950/60 border border-slate-800/80">
            <span className="text-slate-400">P10 Error Quantile:</span>
            <span className="font-semibold text-sky-400">{metrics?.p10_error?.toLocaleString()} MW</span>
          </div>
          <div className="flex justify-between items-center p-2 rounded-lg bg-slate-950/60 border border-slate-800/80">
            <span className="text-slate-400">P50 Median Error:</span>
            <span className="font-semibold text-slate-200">{metrics?.p50_error?.toLocaleString()} MW</span>
          </div>
          <div className="flex justify-between items-center p-2 rounded-lg bg-slate-950/60 border border-slate-800/80">
            <span className="text-slate-400">Max Over-Forecast:</span>
            <span className="font-semibold text-rose-400">+{metrics?.max_over_forecast?.toLocaleString()} MW</span>
          </div>
          <div className="flex justify-between items-center p-2 rounded-lg bg-slate-950/60 border border-slate-800/80">
            <span className="text-slate-400">Max Under-Forecast:</span>
            <span className="font-semibold text-sky-400">{metrics?.max_under_forecast?.toLocaleString()} MW</span>
          </div>
        </CardContent>
      </Card>

      {/* Visualizations Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Chart 1: Error Distribution Histogram */}
        <Card className="border-slate-800 bg-slate-900/80">
          <CardHeader>
            <CardTitle className="text-base text-white flex items-center gap-2">
              <BarChart3 className="h-4 w-4 text-emerald-400" />
              Forecast Error Distribution (MW Bins)
            </CardTitle>
            <CardDescription>
              Histogram of (Forecast - Actual). Positive values indicate over-forecast; negative values indicate under-forecast.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[300px] w-full pt-2">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={distribution?.distribution || []} margin={{ top: 10, right: 10, left: 0, bottom: 25 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                  <XAxis
                    dataKey="bin_label"
                    stroke="#64748b"
                    angle={-45}
                    textAnchor="end"
                    tick={{ fontSize: 9 }}
                  />
                  <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
                  <Tooltip content={<DistTooltip />} />
                  <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                    {distribution?.distribution?.map((entry, index) => {
                      const isOver = entry.bin_start >= 0
                      return (
                        <Cell
                          key={`cell-${index}`}
                          fill={isOver ? "#f43f5e" : "#0ea5e9"}
                          fillOpacity={0.8}
                        />
                      )
                    })}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className="flex justify-center gap-6 text-xs text-slate-400 mt-2">
              <span className="flex items-center gap-1.5">
                <span className="h-2.5 w-2.5 rounded bg-sky-500" />
                Under-forecast (F &lt; A)
              </span>
              <span className="flex items-center gap-1.5">
                <span className="h-2.5 w-2.5 rounded bg-rose-500" />
                Over-forecast (F &gt; A)
              </span>
            </div>
          </CardContent>
        </Card>

        {/* Chart 2: 24-Hour Diurnal Error & Bias Profile */}
        <Card className="border-slate-800 bg-slate-900/80">
          <CardHeader>
            <CardTitle className="text-base text-white flex items-center gap-2">
              <Activity className="h-4 w-4 text-teal-400" />
              Diurnal 24-Hour Error & Bias Profile
            </CardTitle>
            <CardDescription>
              Mean Absolute Error (MAE) and Mean Bias across the 24 hours of the day to identify peak intra-day uncertainty.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[300px] w-full pt-2">
              <ResponsiveContainer width="100%" height="100%">
                <ComposedChart data={hourlyProfile} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                  <XAxis dataKey="hour" stroke="#64748b" tick={{ fontSize: 10 }} tickFormatter={(h) => `${h}:00`} />
                  <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
                  <Tooltip
                    contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155", borderRadius: "8px", fontSize: "12px" }}
                  />
                  <Legend wrapperStyle={{ fontSize: "11px", paddingTop: "8px" }} />
                  <Bar dataKey="mae" fill="#10b981" fillOpacity={0.7} name="MAE (MW)" radius={[4, 4, 0, 0]} />
                  <Line type="monotone" dataKey="mbe" stroke="#f59e0b" strokeWidth={2.5} name="Mean Bias MBE (MW)" />
                  <ReferenceLine y={0} stroke="#64748b" strokeDasharray="3 3" />
                </ComposedChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Chart 3: Daily Timeline Across Month */}
      <Card className="border-slate-800 bg-slate-900/80">
        <CardHeader>
          <CardTitle className="text-base text-white flex items-center gap-2">
            <TrendingUp className="h-4 w-4 text-emerald-400" />
            Daily Accuracy Progression (January 2026)
          </CardTitle>
          <CardDescription>
            Day-by-day Mean Absolute Error (MAE) and Root Mean Squared Error (RMSE) across the entire month.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-[320px] w-full pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={dailyTimeline} margin={{ top: 10, right: 15, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                <XAxis
                  dataKey="date"
                  stroke="#64748b"
                  tick={{ fontSize: 10 }}
                  tickFormatter={(d) => d.split("-").slice(1).join("/")}
                />
                <YAxis stroke="#64748b" tick={{ fontSize: 11 }} tickFormatter={(v) => `${(v/1000).toFixed(1)}k MW`} />
                <Tooltip
                  contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155", borderRadius: "8px", fontSize: "12px" }}
                />
                <Legend wrapperStyle={{ fontSize: "11px", paddingTop: "8px" }} />
                <Line
                  type="monotone"
                  dataKey="mae"
                  stroke="#10b981"
                  strokeWidth={2.5}
                  name="Daily MAE (MW)"
                  dot={{ r: 2 }}
                />
                <Line
                  type="monotone"
                  dataKey="rmse"
                  stroke="#0ea5e9"
                  strokeWidth={2}
                  strokeDasharray="4 4"
                  name="Daily RMSE (MW)"
                  dot={{ r: 2 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
