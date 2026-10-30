import React, { useState } from "react"
import { Wind, RefreshCw, Zap, Clock, ShieldCheck, Database } from "lucide-react"
import { Button } from "./ui/button"
import { Badge } from "./ui/badge"

export function Header({ syncStatus, onSync, isSyncing }) {
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
                National Wind Forecast & Balancing Accuracy Intelligence · Jan 2026
              </p>
            </div>
          </div>

          {/* Quick Metrics & Actions */}
          <div className="flex items-center space-x-3">
            <div className="hidden md:flex items-center space-x-4 text-xs text-slate-400 mr-2 bg-slate-900/80 px-3 py-1.5 rounded-lg border border-slate-800">
              <div className="flex items-center space-x-1.5">
                <Database className="h-3.5 w-3.5 text-emerald-400" />
                <span>Elexon BMRS:</span>
                <span className="text-slate-200 font-medium">FUELHH & WINDFOR</span>
              </div>
              <div className="h-3 w-px bg-slate-800" />
              <div className="flex items-center space-x-1.5">
                <ShieldCheck className="h-3.5 w-3.5 text-teal-400" />
                <span>Status:</span>
                <span className="text-emerald-400 font-medium">Synchronized</span>
              </div>
            </div>

            <Button
              variant="outline"
              size="sm"
              onClick={onSync}
              disabled={isSyncing}
              className="gap-2 text-xs border-slate-700 bg-slate-900 hover:bg-slate-800 hover:text-emerald-400"
            >
              <RefreshCw className={`h-3.5 w-3.5 ${isSyncing ? "animate-spin text-emerald-400" : ""}`} />
              <span>{isSyncing ? "Syncing BMRS..." : "Sync Elexon Data"}</span>
            </Button>
          </div>
        </div>
      </div>
    </header>
  )
}
