import { useState, useEffect } from "react"
import { useFormik } from "formik"
import { z } from "zod"
import {
  Download, Search, Filter,
  ChevronLeft, ChevronRight, FileSpreadsheet
} from "lucide-react"

import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "./ui/card"
import { Button } from "./ui/button"
import { Input } from "./ui/input"
import { Select } from "./ui/select"
import { Badge } from "./ui/badge"

const searchSchema = z.object({
  startDate: z.string(),
  endDate: z.string(),
  cutoffTime: z.string(),
  searchQuery: z.string().optional(),
})

export function DataExplorerView({ availableDates, cutoffOptions }) {
  const [loading, setLoading] = useState(false)
  const [dataRows, setDataRows] = useState([])
  const [page, setPage] = useState(1)
  const pageSize = 15

  const formik = useFormik({
    initialValues: {
      startDate: "2026-01-01",
      endDate: "2026-01-31",
      cutoffTime: "11:00",
      searchQuery: "",
    },
    validate: (values) => {
      try {
        searchSchema.parse(values)
        return {}
      } catch (err) {
        return {}
      }
    },
    onSubmit: (values) => {
      fetchDataset(values.startDate, values.endDate, values.cutoffTime)
    },
  })

  const fetchDataset = async (startDate, endDate, cutoffTime) => {
    setLoading(true)
    try {
      // Fetch day-ahead data for all days in range
      const res = await fetch(`/api/v1/metrics/daily-timeline?start_date=${startDate}&end_date=${endDate}&cutoff_time=${cutoffTime}`)
      const timelineData = await res.json()
      
      // Also fetch detailed records by sampling key dates or whole month
      // To provide complete row-level records, we can fetch export CSV or query day-ahead
      const exportRes = await fetch(`/api/v1/export?start_date=${startDate}&end_date=${endDate}&cutoff_time=${cutoffTime}`)
      const csvText = await exportRes.text()
      
      const lines = csvText.trim().split("\n")
      if (lines.length > 1) {
        const headers = lines[0].split(",")
        const parsedRows = lines.slice(1).map((line, idx) => {
          const cols = line.split(",")
          return {
            id: idx,
            date: cols[0],
            hour: cols[1],
            startTime: cols[2],
            actual: cols[3] ? Number(cols[3]) : null,
            forecast: cols[4] ? Number(cols[4]) : null,
            publishTime: cols[5],
            error: cols[6] ? Number(cols[6]) : null,
            absError: cols[7] ? Number(cols[7]) : null,
            pctError: cols[8] ? Number(cols[8]) : null,
            cutoff: cols[9],
          }
        })
        setDataRows(parsedRows)
      }
    } catch (err) {
      console.error("Failed to load dataset rows:", err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchDataset(formik.values.startDate, formik.values.endDate, formik.values.cutoffTime)
  }, [formik.values.startDate, formik.values.endDate, formik.values.cutoffTime])

  // Filter rows based on search query
  const query = formik.values.searchQuery?.toLowerCase() || ""
  const filteredRows = dataRows.filter((r) => {
    if (!query) return true
    return (
      r.date?.toLowerCase().includes(query) ||
      r.hour?.toLowerCase().includes(query) ||
      String(r.error)?.includes(query)
    )
  })

  // Pagination
  const totalPages = Math.ceil(filteredRows.length / pageSize) || 1
  const displayedRows = filteredRows.slice((page - 1) * pageSize, page * pageSize)

  const handleDownloadCsv = () => {
    const url = `/api/v1/export?start_date=${formik.values.startDate}&end_date=${formik.values.endDate}&cutoff_time=${formik.values.cutoffTime}`
    window.open(url, "_blank")
  }

  return (
    <div className="space-y-6">
      {/* Search & Export Header */}
      <Card className="bg-slate-900/70 border-slate-800">
        <CardContent className="p-4 sm:p-5">
          <form onSubmit={formik.handleSubmit} className="flex flex-wrap items-end gap-4">
            <div className="flex-1 min-w-[200px] space-y-1.5">
              <label htmlFor="searchQuery" className="text-xs font-medium text-slate-300 flex items-center gap-1.5">
                <Search className="h-3.5 w-3.5 text-slate-400" />
                Filter by Date or Hour
              </label>
              <Input
                id="searchQuery"
                name="searchQuery"
                placeholder="e.g. 2026-01-15 or 14:00"
                value={formik.values.searchQuery}
                onChange={formik.handleChange}
              />
            </div>

            <div className="w-[140px] space-y-1.5">
              <label htmlFor="startDate" className="text-xs font-medium text-slate-300">
                From Date
              </label>
              <Select
                id="startDate"
                name="startDate"
                value={formik.values.startDate}
                onChange={formik.handleChange}
              >
                {Array.from({ length: 31 }, (_, i) => {
                  const day = String(i + 1).padStart(2, "0")
                  return <option key={`from-${day}`} value={`2026-01-${day}`}>2026-01-{day}</option>
                })}
              </Select>
            </div>

            <div className="w-[140px] space-y-1.5">
              <label htmlFor="endDate" className="text-xs font-medium text-slate-300">
                To Date
              </label>
              <Select
                id="endDate"
                name="endDate"
                value={formik.values.endDate}
                onChange={formik.handleChange}
              >
                {Array.from({ length: 31 }, (_, i) => {
                  const day = String(i + 1).padStart(2, "0")
                  return <option key={`to-${day}`} value={`2026-01-${day}`}>2026-01-{day}</option>
                })}
              </Select>
            </div>

            <div className="w-[200px] space-y-1.5">
              <label htmlFor="cutoffTime" className="text-xs font-medium text-slate-300">
                Cutoff (D-1)
              </label>
              <Select
                id="cutoffTime"
                name="cutoffTime"
                value={formik.values.cutoffTime}
                onChange={formik.handleChange}
              >
                {cutoffOptions?.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </Select>
            </div>

            <Button
              type="button"
              onClick={handleDownloadCsv}
              className="gap-2 bg-emerald-600 hover:bg-emerald-500 text-white font-medium shadow-md shadow-emerald-950/30"
            >
              <FileSpreadsheet className="h-4 w-4" />
              Download CSV
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Table Card */}
      <Card className="border-slate-800 bg-slate-900/80">
        <CardHeader className="flex flex-row items-center justify-between pb-3">
          <div>
            <CardTitle className="text-base text-white">
              National Wind Actuals & Aligned Forecasts Explorer
            </CardTitle>
            <CardDescription>
              Showing {filteredRows.length} aligned hourly observations with full publication timestamps from Elexon BMRS.
            </CardDescription>
          </div>
          <Badge variant="outline" className="text-xs font-mono text-emerald-400 border-emerald-500/30">
            Page {page} of {totalPages}
          </Badge>
        </CardHeader>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left">
              <thead className="bg-slate-950/80 border-b border-slate-800 text-slate-400 font-mono">
                <tr>
                  <th className="p-3">Delivery Date</th>
                  <th className="p-3">Hour</th>
                  <th className="p-3">Forecast (MW)</th>
                  <th className="p-3">Actual (MW)</th>
                  <th className="p-3">Error (F - A)</th>
                  <th className="p-3">Abs Error %</th>
                  <th className="p-3">Forecast Publication Time</th>
                  <th className="p-3">Decision Cutoff</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {displayedRows.map((r) => {
                  const isOver = r.error > 0
                  return (
                    <tr key={`${r.date}-${r.hour}`} className="hover:bg-slate-800/40">
                      <td className="p-3 font-semibold text-slate-200">{r.date}</td>
                      <td className="p-3 text-slate-300">{r.hour}</td>
                      <td className="p-3 text-emerald-400 font-medium">
                        {r.forecast !== null ? r.forecast.toLocaleString() : "—"}
                      </td>
                      <td className="p-3 text-sky-400 font-medium">
                        {r.actual !== null ? r.actual.toLocaleString() : "—"}
                      </td>
                      <td className="p-3">
                        {r.error !== null ? (
                          <span className={`font-semibold ${isOver ? "text-rose-400" : "text-emerald-400"}`}>
                            {isOver ? "+" : ""}{r.error.toLocaleString()} MW
                          </span>
                        ) : "—"}
                      </td>
                      <td className="p-3 text-slate-300">
                        {r.pctError !== null ? `${r.pctError}%` : "—"}
                      </td>
                      <td className="p-3 text-slate-400 text-[11px]">
                        {r.publishTime ? (
                          <span className="text-slate-300">
                            {new Date(r.publishTime).toLocaleString("en-GB", {
                              month: "short", day: "2-digit", hour: "2-digit", minute: "2-digit", timeZone: "UTC"
                            })} UTC
                          </span>
                        ) : "—"}
                      </td>
                      <td className="p-3 text-slate-400">{r.cutoff || "11:00"}</td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>

          {/* Pagination Controls */}
          <div className="flex items-center justify-between p-4 border-t border-slate-800 bg-slate-950/40">
            <div className="text-xs text-slate-400">
              Showing {(page - 1) * pageSize + 1} to {Math.min(page * pageSize, filteredRows.length)} of {filteredRows.length} entries
            </div>
            <div className="flex items-center space-x-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page <= 1}
                className="gap-1 text-xs"
              >
                <ChevronLeft className="h-3.5 w-3.5" />
                Previous
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page >= totalPages}
                className="gap-1 text-xs"
              >
                Next
                <ChevronRight className="h-3.5 w-3.5" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
