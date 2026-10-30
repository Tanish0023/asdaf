import { useState, useEffect } from "react"
import { useFormik } from "formik"
import { z } from "zod"
import {
  BarChart, Bar, LineChart, Line, ComposedChart, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer, Legend, Cell, ReferenceLine
} from "recharts"
import {
  BarChart3, TrendingUp, AlertCircle, Calendar, Clock,
  Gauge, Target, Activity
} from "lucide-react"

import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "./ui/card"
import { Select } from "./ui/select"
import { Alert, AlertTitle, AlertDescription } from "./ui/alert"

// Zod Validation Schema
const filterSchema = z.object({
  startDate: z.string().min(1, "Start date required"),
  endDate: z.string().min(1, "End date required"),
  cutoffTime: z.string().min(1, "Cutoff time required"),
})

export function AccuracyView({ cutoffOptions }) {
  const [loading, setLoading] = useState(false)
  const [metrics, setMetrics] = useState(null)
  const [hourlyProfile, setHourlyProfile] = useState([])
  const [dailyTimeline, setDailyTimeline] = useState([])
  const [distribution, setDistribution] = useState(null)
  const [error, setError] = useState(null)

  const formik = useFormik({
    initialValues: {
      startDate: "2026-01-01",
      endDate: "2026-01-31",
      cutoffTime: "11:00",
    },
    validate: (values) => {
      try {
        filterSchema.parse(values)
        return {}
      } catch (err) {
        if (err instanceof z.ZodError) {
          const errors = {}
          err.errors.forEach((e) => {
            if (e.path[0]) errors[e.path[0]] = e.message
          })
          return errors
        }
        return {}
      }
    },
    onSubmit: (values) => {
      fetchAllMetrics(values.startDate, values.endDate, values.cutoffTime)
    },
  })

  const fetchAllMetrics = async (startDate, endDate, cutoffTime) => {
    setLoading(true)
    setError(null)
    try {
      const q = `start_date=${startDate}&end_date=${endDate}&cutoff_time=${cutoffTime}`
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
    fetchAllMetrics(formik.values.startDate, formik.values.endDate, formik.values.cutoffTime)
  }, [formik.values.startDate, formik.values.endDate, formik.values.cutoffTime])

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

  return (
    <div className="space-y-6">
      {/* Filter Control (Formik + Zod) */}
      <Card className="bg-slate-900/60 border-slate-800">
        <CardContent className="p-4 sm:p-5">
          <form onSubmit={formik.handleSubmit} className="flex flex-wrap items-end gap-4">
            <div className="flex-1 min-w-[160px] space-y-1.5">
              <label htmlFor="startDate" className="text-xs font-medium text-slate-300 flex items-center gap-1.5">
                <Calendar className="h-3.5 w-3.5 text-emerald-400" />
                Start Date
              </label>
              <Select
                id="startDate"
                name="startDate"
                value={formik.values.startDate}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
              >
                {Array.from({ length: 31 }, (_, i) => {
                  const day = String(i + 1).padStart(2, "0")
                  return (
                    <option key={`2026-01-${day}`} value={`2026-01-${day}`}>
                      2026-01-{day}
                    </option>
                  )
                })}
              </Select>
            </div>

            <div className="flex-1 min-w-[160px] space-y-1.5">
              <label htmlFor="endDate" className="text-xs font-medium text-slate-300 flex items-center gap-1.5">
                <Calendar className="h-3.5 w-3.5 text-emerald-400" />
                End Date
              </label>
              <Select
                id="endDate"
                name="endDate"
                value={formik.values.endDate}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
              >
                {Array.from({ length: 31 }, (_, i) => {
                  const day = String(i + 1).padStart(2, "0")
                  return (
                    <option key={`2026-01-${day}`} value={`2026-01-${day}`}>
                      2026-01-{day}
                    </option>
                  )
                })}
              </Select>
            </div>

            <div className="flex-1 min-w-[240px] space-y-1.5">
              <label htmlFor="cutoffTime" className="text-xs font-medium text-slate-300 flex items-center gap-1.5">
                <Clock className="h-3.5 w-3.5 text-sky-400" />
                Decision Gate Closure (D-1)
              </label>
              <Select
                id="cutoffTime"
                name="cutoffTime"
                value={formik.values.cutoffTime}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
              >
                {cutoffOptions?.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </Select>
            </div>

            <div className="hidden xl:flex items-center text-xs text-slate-400 bg-slate-950/60 px-4 py-2 rounded-lg border border-slate-800 mb-0.5">
              <span>
                Evaluating <strong className="text-emerald-400">{metrics?.total_observations || 0}</strong> hourly delivery intervals across January 2026
              </span>
            </div>
          </form>
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

        {/* P90 Shortfall */}
        <Card className="bg-slate-900/80 border-slate-800 p-4 relative overflow-hidden">
          <div className="text-[11px] text-slate-400 font-medium">P90 Shortfall Risk</div>
          <div className="text-2xl font-bold font-mono text-rose-400 mt-1">
            {metrics?.p90_shortfall?.toLocaleString() ?? "—"}{" "}
            <span className="text-xs font-normal text-slate-400">MW</span>
          </div>
          <div className="text-[10px] text-slate-500 mt-1">
            Reserve buffer for 90% protection
          </div>
        </Card>

        {/* P95 Shortfall */}
        <Card className="bg-slate-900/80 border-slate-800 p-4 relative overflow-hidden">
          <div className="text-[11px] text-slate-400 font-medium">P95 Shortfall Risk</div>
          <div className="text-2xl font-bold font-mono text-orange-400 mt-1">
            {metrics?.p95_shortfall?.toLocaleString() ?? "—"}{" "}
            <span className="text-xs font-normal text-slate-400">MW</span>
          </div>
          <div className="text-[10px] text-slate-500 mt-1">
            Reserve buffer for 95% protection
          </div>
        </Card>
      </div>

      {/* Quantiles & Extremes Secondary Bar */}
      <Card className="bg-slate-900/50 border-slate-800">
        <CardContent className="p-4 grid grid-cols-2 md:grid-cols-4 gap-4 text-xs font-mono">
          <div className="flex justify-between items-center p-2 rounded-lg bg-slate-950/60 border border-slate-800/80">
            <span className="text-slate-400">P10 Error (Under-forecast):</span>
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
              Histogram of (Forecast - Actual). Bins right of 0 represent wind shortfall (over-forecast); bins left represent surplus.
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
                      const isShortfall = entry.bin_start >= 0
                      return (
                        <Cell
                          key={`cell-${index}`}
                          fill={isShortfall ? "#f43f5e" : "#0ea5e9"}
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
                Under-forecast (Wind Surplus)
              </span>
              <span className="flex items-center gap-1.5">
                <span className="h-2.5 w-2.5 rounded bg-rose-500" />
                Over-forecast (Wind Shortfall)
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
