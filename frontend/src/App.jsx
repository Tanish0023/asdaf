import { useState, useEffect } from "react"
import { Calendar, BarChart3 } from "lucide-react"

import { Header } from "./components/Header"
import { DayAheadView } from "./components/DayAheadView"
import { AccuracyView } from "./components/AccuracyView"
import { Tabs, TabsList, TabsTrigger, TabsContent } from "./components/ui/tabs"

export default function App() {
  const [activeTab, setActiveTab] = useState("day-ahead")
  const [dateInfo, setDateInfo] = useState(null)

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

  return (
    <div className="min-h-screen bg-[#080d1a] text-slate-100 flex flex-col font-sans">
      {/* Top Header */}
      <Header />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
        {/* Primary Tabs Navigation */}
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
            </TabsList>
          </div>

          {/* Tab 1: Day-Ahead Procurement View */}
          <TabsContent value="day-ahead">
            <DayAheadView availableDates={dateInfo} />
          </TabsContent>

          {/* Tab 2: Quantitative Accuracy Evaluation */}
          <TabsContent value="accuracy">
            <AccuracyView />
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
          </div>
        </div>
      </footer>
    </div>
  )
}
