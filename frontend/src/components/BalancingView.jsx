import { useState, useEffect } from "react"
import { useFormik } from "formik"
import { z } from "zod"
import {
  ComposedChart, Line, Bar, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer, Legend, ReferenceLine
} from "recharts"
import {
  ShieldAlert, ShieldCheck, Zap, Flame, Wind,
  AlertTriangle
} from "lucide-react"

import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "./ui/card"
import { Input } from "./ui/input"
import { Select } from "./ui/select"
import { Badge } from "./ui/badge"
import { Alert, AlertTitle, AlertDescription } from "./ui/alert"

// Zod Validation Schema
const calcSchema = z.object({
  customerDemand: z
    .number({ invalid_type_error: "Must be a valid number" })
    .min(500, "Demand must be at least 500 MW")
    .max(100000, "Demand cannot exceed 100,000 MW"),
  deliveryDate: z.string().min(1, "Delivery date required"),
  cutoffTime: z.string().min(1, "Cutoff time required"),
  confidenceLevel: z.number(),
})

export function BalancingView({ availableDates, cutoffOptions }) {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const formik = useFormik({
    initialValues: {
      customerDemand: 25000,
      deliveryDate: availableDates?.default_delivery_date || "2026-01-15",
      cutoffTime: "11:00",
      confidenceLevel: 0.90,
    },
    validate: (values) => {
      try {
        calcSchema.parse(values)
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
    onSubmit: async (values) => {
      setLoading(true)
      setError(null)
      try {
        const res = await fetch("/api/v1/metrics/balancing-calculator", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            customer_demand_mw: Number(values.customerDemand),
            delivery_date: values.deliveryDate,
            cutoff_time: values.cutoffTime,
            confidence_level: Number(values.confidenceLevel),
          }),
        })

        if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`)
        const data = await res.json()
        setResult(data)
      } catch (err) {
        setError(err.message || "Failed to calculate balancing requirements")
      } finally {
        setLoading(false)
      }
    },
  })

  useEffect(() => {
    formik.submitForm()
  }, [formik.values.deliveryDate, formik.values.cutoffTime, formik.values.confidenceLevel])

  const chartData = result?.hourly_breakdown?.map((h) => ({
    hour: h.hour,
    demand: h.demand_mw,
    forecastWind: h.forecast_wind_mw,
    actualWind: h.actual_wind_mw,
    baseThermal: h.base_thermal_required_mw,
    reserveBuffer: h.reserve_buffer_mw,
    totalProcured: h.total_thermal_procured_mw,
    netPosition: h.net_position_with_actual_mw,
  })) || []

  return (
    <div className="space-y-6">
      {/* Input Parameters Form (Formik + Zod) */}
      <Card className="bg-slate-900/70 border-slate-800">
        <CardHeader className="pb-3">
          <CardTitle className="text-base text-white flex items-center gap-2">
            <ShieldCheck className="h-4 w-4 text-emerald-400" />
            Wholesale Day-Ahead Thermal Procurement & Sizing Calculator
          </CardTitle>
          <CardDescription>
            Compute expected thermal power procurement beyond wind, plus a statistical reserve buffer derived from historical wind shortfall errors.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={formik.handleSubmit} className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Customer Demand Input */}
            <div className="space-y-1.5">
              <label htmlFor="customerDemand" className="text-xs font-medium text-slate-300 flex items-center gap-1">
                <Zap className="h-3.5 w-3.5 text-amber-400" />
                Consumer Electricity Demand (MW)
              </label>
              <Input
                id="customerDemand"
                name="customerDemand"
                type="number"
                step="500"
                value={formik.values.customerDemand}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                className={formik.touched.customerDemand && formik.errors.customerDemand ? "border-rose-500" : ""}
              />
              {formik.touched.customerDemand && formik.errors.customerDemand && (
                <p className="text-[11px] text-rose-400">{formik.errors.customerDemand}</p>
              )}
            </div>

            {/* Target Delivery Date */}
            <div className="space-y-1.5">
              <label htmlFor="deliveryDate" className="text-xs font-medium text-slate-300">
                Target Delivery Date
              </label>
              <Select
                id="deliveryDate"
                name="deliveryDate"
                value={formik.values.deliveryDate}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
              >
                {availableDates?.delivery_dates?.map((d) => (
                  <option key={d} value={d}>
                    {d}
                  </option>
                ))}
              </Select>
            </div>

            {/* Cutoff Time */}
            <div className="space-y-1.5">
              <label htmlFor="cutoffTime" className="text-xs font-medium text-slate-300">
                Gate Closure Cutoff (D-1)
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

            {/* Confidence Level */}
            <div className="space-y-1.5">
              <label htmlFor="confidenceLevel" className="text-xs font-medium text-slate-300">
                Wind Shortfall Protection Level
              </label>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => formik.setFieldValue("confidenceLevel", 0.90)}
                  className={`flex-1 py-1.5 px-3 rounded-lg text-xs font-semibold border transition-all ${
                    formik.values.confidenceLevel === 0.90
                      ? "bg-emerald-600 text-white border-emerald-500 shadow-md"
                      : "bg-slate-900 text-slate-400 border-slate-700 hover:bg-slate-800"
                  }`}
                >
                  90% (P90 Risk)
                </button>
                <button
                  type="button"
                  onClick={() => formik.setFieldValue("confidenceLevel", 0.95)}
                  className={`flex-1 py-1.5 px-3 rounded-lg text-xs font-semibold border transition-all ${
                    formik.values.confidenceLevel === 0.95
                      ? "bg-amber-600 text-white border-amber-500 shadow-md"
                      : "bg-slate-900 text-slate-400 border-slate-700 hover:bg-slate-800"
                  }`}
                >
                  95% (P95 Risk)
                </button>
              </div>
            </div>
          </form>
        </CardContent>
      </Card>

      {error && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>Calculation Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Primary Results Comparison Cards: CLEAR DISTINCTION */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Expected Base Thermal Requirement */}
        <Card className="bg-slate-900/80 border-slate-800 p-5 relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400 font-semibold uppercase tracking-wider">
              1. Base Thermal Procurement
            </span>
            <Badge variant="outline" className="border-sky-500/40 text-sky-400 text-[10px]">
              Expected Shortfall
            </Badge>
          </div>
          <div className="text-3xl font-extrabold font-mono text-sky-400 mt-2">
            {result?.expected_base_thermal_mw?.toLocaleString() ?? "—"}{" "}
            <span className="text-sm font-normal text-slate-400">MW</span>
          </div>
          <p className="text-xs text-slate-400 mt-2 leading-relaxed">
            Directly needed to serve demand beyond expected wind (Demand {result?.customer_demand_mw?.toLocaleString()} MW minus Avg Forecast {result?.avg_forecast_wind_mw?.toLocaleString()} MW).
          </p>
          <div className="absolute top-2 right-2 text-slate-800/40 pointer-events-none">
            <Flame className="h-16 w-16 stroke-1" />
          </div>
        </Card>

        {/* Recommended Reserve Buffer */}
        <Card className="bg-slate-900/80 border-slate-800 p-5 relative overflow-hidden ring-1 ring-amber-500/30">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400 font-semibold uppercase tracking-wider">
              2. Recommended Reserve Buffer
            </span>
            <Badge variant="warning" className="text-[10px]">
              {result ? `${Math.round(result.confidence_level * 100)}% Confidence` : "—"}
            </Badge>
          </div>
          <div className="text-3xl font-extrabold font-mono text-amber-400 mt-2">
            +{result?.recommended_reserve_buffer_mw?.toLocaleString() ?? "—"}{" "}
            <span className="text-sm font-normal text-slate-400">MW</span>
          </div>
          <p className="text-xs text-slate-400 mt-2 leading-relaxed">
            Additional reserve cushion to cover historical wind forecast error shortfall at the {result ? Math.round(result.confidence_level * 100) : 90}th percentile.
          </p>
          <div className="absolute top-2 right-2 text-slate-800/40 pointer-events-none">
            <ShieldAlert className="h-16 w-16 stroke-1" />
          </div>
        </Card>

        {/* Total Thermal Procurement Target */}
        <Card className="bg-emerald-950/20 border-emerald-600/30 p-5 relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs text-emerald-400 font-semibold uppercase tracking-wider">
              3. Total Procurement Target
            </span>
            <Badge variant="success" className="text-[10px]">
              Recommended Action
            </Badge>
          </div>
          <div className="text-3xl font-extrabold font-mono text-emerald-400 mt-2">
            {result?.total_thermal_procurement_mw?.toLocaleString() ?? "—"}{" "}
            <span className="text-sm font-normal text-slate-400">MW</span>
          </div>
          <p className="text-xs text-slate-400 mt-2 leading-relaxed">
            Sum of Base Thermal ({result?.expected_base_thermal_mw?.toLocaleString()} MW) + Quantified Reserve ({result?.recommended_reserve_buffer_mw?.toLocaleString()} MW) to guarantee consumer supply.
          </p>
          <div className="absolute top-2 right-2 text-emerald-900/40 pointer-events-none">
            <ShieldCheck className="h-16 w-16 stroke-1" />
          </div>
        </Card>
      </div>

      {/* Hourly Balancing Dispatch Simulation Chart */}
      <Card className="border-slate-800 bg-slate-900/80">
        <CardHeader>
          <CardTitle className="text-base text-white flex items-center gap-2">
            <Zap className="h-4 w-4 text-emerald-400" />
            24-Hour Energy Balance & Reserve Protection Simulation
          </CardTitle>
          <CardDescription>
            Visualizing Customer Demand vs Forecast Wind, Base Thermal, and the Recommended Reserve Buffer across all 24 delivery hours.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-[360px] w-full pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={chartData} margin={{ top: 15, right: 15, left: 10, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                <XAxis dataKey="hour" stroke="#64748b" tick={{ fontSize: 10 }} />
                <YAxis
                  stroke="#64748b"
                  tick={{ fontSize: 11 }}
                  tickFormatter={(val) => `${(val / 1000).toFixed(0)}k MW`}
                />
                <Tooltip
                  contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155", borderRadius: "8px", fontSize: "12px" }}
                />
                <Legend wrapperStyle={{ fontSize: "11px", paddingTop: "8px" }} />
                <ReferenceLine
                  y={formik.values.customerDemand}
                  stroke="#f59e0b"
                  strokeDasharray="4 4"
                  strokeWidth={2}
                  label={{ value: `Demand: ${formik.values.customerDemand} MW`, fill: "#f59e0b", fontSize: 11, position: "top" }}
                />
                <Bar
                  dataKey="forecastWind"
                  stackId="supply"
                  fill="#10b981"
                  name="Forecast Wind Generation (MW)"
                />
                <Bar
                  dataKey="baseThermal"
                  stackId="supply"
                  fill="#0ea5e9"
                  name="Base Thermal Required (MW)"
                />
                <Bar
                  dataKey="reserveBuffer"
                  stackId="supply"
                  fill="#f43f5e"
                  fillOpacity={0.8}
                  name="Reserve Buffer for Shortfall (MW)"
                />
                <Line
                  type="monotone"
                  dataKey="actualWind"
                  stroke="#a855f7"
                  strokeWidth={2.5}
                  name="Actual Wind Generation (MW)"
                  dot={false}
                />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
