import { useState, useEffect } from "react"
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer
} from "recharts"
import {
  Calendar, Clock, AlertTriangle, ArrowUpRight, ArrowDownRight,
  Info, TrendingUp
} from "lucide-react"

import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "./ui/card"
import { Select } from "./ui/select"
import { Badge } from "./ui/badge"
import { Alert, AlertTitle, AlertDescription } from "./ui/alert"

export function DayAheadView({ availableDates }) {
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)
  const [deliveryDate, setDeliveryDate] = useState(
    availableDates?.default_delivery_date || "2026-01-15"
  )

  // Update default delivery date when availableDates finishes loading
  useEffect(() => {
    if (availableDates?.default_delivery_date && !deliveryDate) {
      setDeliveryDate(availableDates.default_delivery_date)
    }
  }, [availableDates, deliveryDate])

  const fetchDayAhead = async (targetDate) => {
    if (!targetDate) return
    setLoading(true)
    setError(null)
    try {
      const res = await fetch(`/api/v1/day-ahead?delivery_date=${targetDate}`)
      if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`)
      const result = await res.json()
      setData(result)
    } catch (err) {
      setError(err.message || "Failed to load day-ahead forecast data")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchDayAhead(deliveryDate)
  }, [deliveryDate])

  const chartData = data?.hourly_records?.map((r) => ({
    hour: r.hour,
    actual: r.actual_generation,
    forecast: r.forecast_generation,
    error: r.error_mw,
    absError: r.abs_error_mw,
    publishTime: r.publish_time,
    periods: r.settlementPeriods?.join(", ") || "",
  })) || []

  const summary = data?.summary || {}

  // Custom Chart Tooltip
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const item = payload[0].payload
      const isOver = item.error > 0
      return (
        <div className="bg-slate-900/95 border border-slate-700/80 p-3.5 rounded-xl shadow-2xl backdrop-blur-md text-xs space-y-1.5 min-w-[220px]">
          <div className="flex items-center justify-between border-b border-slate-800 pb-1.5 mb-1.5">
            <span className="font-semibold text-white text-sm">Delivery Hour: {label}</span>
            <Badge variant="outline" className="text-[10px] text-slate-400">
              Periods {item.periods}
            </Badge>
          </div>
          <div className="flex justify-between items-center text-slate-300">
            <span className="flex items-center gap-1.5">
              <span className="h-2 w-2 rounded-full bg-emerald-400" />
              Day-Ahead Forecast:
            </span>
            <span className="font-mono font-semibold text-emerald-400">
              {item.forecast !== null ? `${item.forecast.toLocaleString()} MW` : "N/A"}
            </span>
          </div>
          <div className="flex justify-between items-center text-slate-300">
            <span className="flex items-center gap-1.5">
              <span className="h-2 w-2 rounded-full bg-sky-400" />
              Actual Generation:
            </span>
            <span className="font-mono font-semibold text-sky-400">
              {item.actual !== null ? `${item.actual.toLocaleString()} MW` : "N/A"}
            </span>
          </div>
          <div className="border-t border-slate-800 pt-1.5 mt-1.5 flex justify-between items-center font-mono">
            <span className="text-slate-400">Forecast Error (F - A):</span>
            <span className={`font-semibold ${isOver ? "text-rose-400" : "text-emerald-400"}`}>
              {item.error !== null ? `${item.error > 0 ? "+" : ""}${item.error.toLocaleString()} MW` : "N/A"}
            </span>
          </div>
          {item.publishTime && (
            <div className="text-[10px] text-slate-500 pt-1 flex items-center gap-1">
              <Clock className="h-3 w-3" />
              Published: {new Date(item.publishTime).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} UTC
            </div>
          )}
        </div>
      )
    }
    return null
  }

  return (
    <div className="space-y-6">
      {/* Control Panel */}
      <Card className="bg-slate-900/60 border-slate-800">
        <CardContent className="p-4 sm:p-5">
          <div className="flex flex-wrap items-center justify-between gap-4">
            {/* Delivery Date Selection */}
            <div className="w-full sm:w-auto sm:min-w-[260px] space-y-1.5">
              <label htmlFor="deliveryDate" className="text-xs font-medium text-slate-300 flex items-center gap-1.5">
                <Calendar className="h-3.5 w-3.5 text-emerald-400" />
                Target Delivery Date (Day D)
              </label>
              <Select
                id="deliveryDate"
                value={deliveryDate}
                onChange={(e) => setDeliveryDate(e.target.value)}
              >
                {availableDates?.delivery_dates?.map((d) => (
                  <option key={d} value={d} className="bg-slate-900 text-white">
                    {d} ({new Date(d).toLocaleDateString("en-GB", { weekday: "short" })})
                  </option>
                ))}
              </Select>
            </div>

            {/* Decision Cutoff Plain Text Banner */}
            <div className="flex items-center text-xs text-slate-300 bg-slate-950/80 px-4 py-2.5 rounded-lg border border-slate-800">
              <Clock className="h-4 w-4 text-emerald-400 mr-2 shrink-0" />
              <span>
                Decision Cutoff: <strong className="text-emerald-400">{data?.cutoff_time || "11:00"} UTC</strong> on D-1 (<strong className="text-slate-200">{data?.decision_date || "D-1"}</strong>)
              </span>
            </div>
          </div>
        </CardContent>
      </Card>

      {error && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>Error Loading Data</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* KPI Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 sm:gap-4">
        <Card className="bg-slate-900/70 border-slate-800/80 p-4">
          <div className="text-[11px] text-slate-400 font-medium">Avg Forecast Wind</div>
          <div className="text-lg sm:text-xl font-bold font-mono text-emerald-400 mt-1">
            {summary.avg_forecast_mw?.toLocaleString() || "—"}{" "}
            <span className="text-xs font-normal text-slate-400">MW</span>
          </div>
          <div className="text-[10px] text-slate-500 mt-0.5">
            Peak: {summary.max_forecast_mw?.toLocaleString() || "—"} MW
          </div>
        </Card>

        <Card className="bg-slate-900/70 border-slate-800/80 p-4">
          <div className="text-[11px] text-slate-400 font-medium">Avg Actual Wind</div>
          <div className="text-lg sm:text-xl font-bold font-mono text-sky-400 mt-1">
            {summary.avg_actual_mw?.toLocaleString() || "—"}{" "}
            <span className="text-xs font-normal text-slate-400">MW</span>
          </div>
          <div className="text-[10px] text-slate-500 mt-0.5">
            Total: {summary.total_actual_mwh ? `${Math.round(summary.total_actual_mwh / 1000)} GWh` : "—"}
          </div>
        </Card>

        <Card className="bg-slate-900/70 border-slate-800/80 p-4">
          <div className="text-[11px] text-slate-400 font-medium">Daily MAE</div>
          <div className="text-lg sm:text-xl font-bold font-mono text-amber-400 mt-1">
            {summary.mae_mw?.toLocaleString() || "—"}{" "}
            <span className="text-xs font-normal text-slate-400">MW</span>
          </div>
          <div className="text-[10px] text-slate-500 mt-0.5">Mean Absolute Error</div>
        </Card>

        <Card className="bg-slate-900/70 border-slate-800/80 p-4">
          <div className="text-[11px] text-slate-400 font-medium">Mean Bias (MBE)</div>
          <div className={`text-lg sm:text-xl font-bold font-mono mt-1 ${summary.mbe_mw > 0 ? "text-rose-400" : "text-emerald-400"}`}>
            {summary.mbe_mw ? `${summary.mbe_mw > 0 ? "+" : ""}${summary.mbe_mw.toLocaleString()}` : "—"}{" "}
            <span className="text-xs font-normal text-slate-400">MW</span>
          </div>
          <div className="text-[10px] text-slate-500 mt-0.5">
            {summary.mbe_mw > 0 ? "Over-forecast (F > A)" : "Under-forecast (F < A)"}
          </div>
        </Card>

        <Card className="bg-slate-900/70 border-slate-800/80 p-4">
          <div className="text-[11px] text-slate-400 font-medium">WAPE Error Rate</div>
          <div className="text-lg sm:text-xl font-bold font-mono text-slate-100 mt-1">
            {summary.wape_pct !== undefined ? `${summary.wape_pct}%` : "—"}
          </div>
          <div className="text-[10px] text-slate-500 mt-0.5">Weighted % of Actuals</div>
        </Card>

        <Card className="bg-slate-900/70 border-slate-800/80 p-4">
          <div className="text-[11px] text-slate-400 font-medium">Alignment Cutoff</div>
          <div className="text-lg sm:text-xl font-bold font-mono text-teal-400 mt-1">
            {data?.cutoff_time || "11:00"}
          </div>
          <div className="text-[10px] text-slate-500 mt-0.5">Strict D-1 Gate Filter</div>
        </Card>
      </div>

      {/* Interactive Generation Chart */}
      <Card className="border-slate-800 bg-slate-900/80">
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <div>
            <CardTitle className="text-base text-white flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-emerald-400" />
              Day-Ahead Wind Generation vs Actuals ({data?.delivery_date})
            </CardTitle>
            <CardDescription>
              Comparing latest WINDFOR forecast available at {data?.cutoff_time} UTC (D-1) against aggregated FUELHH actual generation.
            </CardDescription>
          </div>
          <div className="flex items-center gap-3 text-xs">
            <div className="flex items-center gap-1.5 text-emerald-400">
              <span className="h-3 w-3 rounded-sm bg-emerald-500/30 border border-emerald-500 inline-block" />
              Day-Ahead Forecast
            </div>
            <div className="flex items-center gap-1.5 text-sky-400">
              <span className="h-3 w-3 rounded-sm bg-sky-500/30 border border-sky-500 inline-block" />
              Actual Generation
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="h-[360px] w-full pt-4">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData} margin={{ top: 10, right: 10, left: 10, bottom: 0 }}>
                <defs>
                  <linearGradient id="forecastGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0.0} />
                  </linearGradient>
                  <linearGradient id="actualGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                <XAxis dataKey="hour" stroke="#64748b" tick={{ fontSize: 11 }} />
                <YAxis
                  stroke="#64748b"
                  tick={{ fontSize: 11 }}
                  tickFormatter={(val) => `${(val / 1000).toFixed(0)}k MW`}
                />
                <Tooltip content={<CustomTooltip />} />
                <Area
                  type="monotone"
                  dataKey="forecast"
                  stroke="#10b981"
                  strokeWidth={2.5}
                  fillOpacity={1}
                  fill="url(#forecastGrad)"
                  name="Forecast Wind"
                />
                <Area
                  type="monotone"
                  dataKey="actual"
                  stroke="#0ea5e9"
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#actualGrad)"
                  name="Actual Wind"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Hourly Breakdown Table */}
      <Card className="border-slate-800 bg-slate-900/60">
        <CardHeader>
          <CardTitle className="text-sm font-semibold text-white">
            Hourly Schedule & Forecast Audit Log
          </CardTitle>
          <CardDescription>
            Audit trail of the specific forecast publish time selected for each delivery hour.
          </CardDescription>
        </CardHeader>
        <CardContent className="p-0">
          <div className="max-h-[360px] overflow-auto">
            <table className="w-full text-xs text-left">
              <thead className="bg-slate-950/80 sticky top-0 border-b border-slate-800 text-slate-400 font-mono">
                <tr>
                  <th className="p-3">Delivery Hour</th>
                  <th className="p-3">Settlement Periods</th>
                  <th className="p-3">Forecast (MW)</th>
                  <th className="p-3">Actual (MW)</th>
                  <th className="p-3">Forecast Error (F - A)</th>
                  <th className="p-3">Abs Error %</th>
                  <th className="p-3">Forecast Publish Time</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {data?.hourly_records?.map((r) => {
                  const isOver = r.error_mw > 0
                  return (
                    <tr key={r.hour} className="hover:bg-slate-800/40">
                      <td className="p-3 font-semibold text-slate-200">{r.hour}</td>
                      <td className="p-3 text-slate-400">{r.settlementPeriods?.join(", ")}</td>
                      <td className="p-3 text-emerald-400 font-medium">
                        {r.forecast_generation?.toLocaleString() ?? "—"}
                      </td>
                      <td className="p-3 text-sky-400 font-medium">
                        {r.actual_generation?.toLocaleString() ?? "—"}
                      </td>
                      <td className="p-3">
                        {r.error_mw !== null ? (
                          <span className={`inline-flex items-center gap-1 font-semibold ${isOver ? "text-rose-400" : "text-emerald-400"}`}>
                            {isOver ? <ArrowUpRight className="h-3 w-3" /> : <ArrowDownRight className="h-3 w-3" />}
                            {isOver ? "+" : ""}{r.error_mw.toLocaleString()} MW
                          </span>
                        ) : "—"}
                      </td>
                      <td className="p-3 text-slate-300">
                        {r.pct_error !== null ? `${r.pct_error}%` : "—"}
                      </td>
                      <td className="p-3 text-slate-400 text-[11px]">
                        {r.publish_time ? (
                          <span className="text-slate-300">
                            {new Date(r.publish_time).toLocaleString("en-GB", {
                              month: "short", day: "2-digit", hour: "2-digit", minute: "2-digit", timeZone: "UTC"
                            })} UTC
                          </span>
                        ) : "—"}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
