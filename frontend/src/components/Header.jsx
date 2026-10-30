import { Wind } from "lucide-react"
import { Badge } from "./ui/badge"

export function Header() {
  return (
    <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Brand */}
          <div className="flex items-center space-x-3">
            <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-400 flex items-center justify-center shadow-lg shadow-emerald-950/40">
              <Wind className="h-6 w-6 text-white" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-lg font-bold tracking-tight text-white">GridBricks</span>
                <span className="text-xs px-2 py-0.5 rounded-md bg-emerald-500/20 text-emerald-400 font-semibold border border-emerald-500/30">
                  WindPulse
                </span>
                <Badge variant="outline" className="hidden sm:inline-flex text-[10px] text-slate-400 border-slate-800">
                  UK Day-Ahead Wholesale Desk
                </Badge>
              </div>
              <p className="text-[11px] text-slate-400">
                National Wind Forecast & Accuracy Evaluation · Jan 2026
              </p>
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}
