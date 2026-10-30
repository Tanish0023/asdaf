import React, { useState, useEffect } from "react"
import {
  Calendar, BarChart3, ShieldCheck, Database,
  TrendingUp, RefreshCw, CheckCircle2, AlertTriangle, FileSpreadsheet
} from "lucide-react"

import { Header } from "./components/Header"
import { DayAheadView } from "./components/DayAheadView"
import { AccuracyView } from "./components/AccuracyView"
import { BalancingView } from "./components/BalancingView"
import { DataExplorerView } from "./components/DataExplorerView"
import { Tabs, TabsList, TabsTrigger, TabsContent } from "./components/ui/tabs"
import { Alert, AlertTitle, AlertDescription } from "./components/ui/alert"

export default function App() {
  const [activeTab, setActiveTab] = useState("day-ahead")
  const [dateInfo, setDateInfo] = useState(null)
  const [isSyncing, setIsSyncing] = useState(false)
  const [syncNotice, setSyncNotice] = useState(null)

  const fetchDates = async () => {
    try {
      const res = await fetch("/api/v1/dates")
      if (res.ok) {
        const data = await res.json()
        setDateInfo(data)
      }
    } catch (err) {
      console.error("Failed to fetch available dates:", err)
    }
  }

  useEffect(() => {
    fetchDates()
  }, [])

  const handleSync = async () => {
    setIsSyncing(true)
    setSyncNotice(null)
    try {
      const res = await fetch("/api/v1/sync", { method: "POST" })
      const data = await res.json()
      if (res.ok) {
        setSyncNotice({
          type: "success",
          title: "Synchronization Successful",
          message: `Successfully refreshed ${data.actuals_synced} actuals and ${data.forecasts_synced} forecasts from Elexon BMRS into Neon PostgreSQL.`,
        })
        fetchDates()
      } else if (res.status === 503) {
        setSyncNotice({
          type: "warning",
          title: "External Elexon Live Endpoint Notice",
          message: data.detail || "External Elexon API is temporarily unreachable (DNS/Network). The platform continues operating without interruption on the pre-cached January 2026 dataset in Neon PostgreSQL.",
        })
      } else {
        throw new Error(data.detail || "Sync failed")
      }
    } catch (err) {
      setSyncNotice({
        type: "error",
        title: "Synchronization Failed",
        message: err.message || "Failed to synchronize with Elexon API. The platform continues operating using cached data in Neon PostgreSQL.",
      })
    } finally {
      setIsSyncing(false)
    }
  }

  return (
    <div className="min-h-screen bg-[#080d1a] text-slate-100 flex flex-col font-sans">
      {/* Top Header */}
      <Header syncStatus={dateInfo} onSync={handleSync} isSyncing={isSyncing} />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
        {/* Sync Notification Banner */}
        {syncNotice && (
          <Alert variant={syncNotice.type === "success" ? "success" : syncNotice.type === "warning" ? "warning" : "destructive"}>
            {syncNotice.type === "success" ? (
              <CheckCircle2 className="h-4 w-4" />
            ) : (
              <AlertTriangle className="h-4 w-4" />
            )}
            <AlertTitle>{syncNotice.title || (syncNotice.type === "success" ? "Sync Successful" : "Sync Error")}</AlertTitle>
            <AlertDescription>{syncNotice.message}</AlertDescription>
          </Alert>
        )}

        {/* Primary Tabs Navigation (shadcn tabs) */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <TabsList className="bg-slate-900/90 border border-slate-800">
              <TabsTrigger value="day-ahead" className="gap-2">
                <Calendar className="h-4 w-4 text-emerald-400" />
                <span>Day-Ahead Procurement</span>
              </TabsTrigger>
              <TabsTrigger value="accuracy" className="gap-2">
                <BarChart3 className="h-4 w-4 text-teal-400" />
                <span>Quantitative Accuracy</span>
              </TabsTrigger>
              <TabsTrigger value="balancing" className="gap-2">
                <ShieldCheck className="h-4 w-4 text-amber-400" />
                <span>Risk & Balancing Sizing</span>
              </TabsTrigger>
              <TabsTrigger value="explorer" className="gap-2">
                <Database className="h-4 w-4 text-sky-400" />
                <span>Data Explorer & CSV</span>
              </TabsTrigger>
            </TabsList>
          </div>

          {/* Tab 1: Day-Ahead Procurement View */}
          <TabsContent value="day-ahead">
            <DayAheadView
              availableDates={dateInfo}
              cutoffOptions={dateInfo?.cutoff_options}
            />
          </TabsContent>

          {/* Tab 2: Quantitative Accuracy Evaluation */}
          <TabsContent value="accuracy">
            <AccuracyView cutoffOptions={dateInfo?.cutoff_options} />
          </TabsContent>

          {/* Tab 3: Risk & Balancing Calculator */}
          <TabsContent value="balancing">
            <BalancingView
              availableDates={dateInfo}
              cutoffOptions={dateInfo?.cutoff_options}
            />
          </TabsContent>

          {/* Tab 4: Data Explorer & CSV Export */}
          <TabsContent value="explorer">
            <DataExplorerView
              availableDates={dateInfo}
              cutoffOptions={dateInfo?.cutoff_options}
            />
          </TabsContent>
        </Tabs>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-slate-950/60 py-6 text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center space-x-2">
            <span className="font-semibold text-slate-400">GridBricks WindPulse</span>
            <span>·</span>
            <span>UK National Wind Power Procurement Decision Support</span>
          </div>
          <div className="flex items-center space-x-4 text-slate-400">
            <span>Data: Elexon BMRS (FUELHH & WINDFOR)</span>
            <span>·</span>
            <span>Period: January 2026</span>
            <span>·</span>
            <span className="text-emerald-400 font-medium">Built for Wholesale Energy Trading</span>
          </div>
        </div>
      </footer>
    </div>
  )
}
