import React from 'react'
import { Plane, RefreshCw, Radio, Sparkles, Settings, Send } from 'lucide-react'

export default function Header({ onTriggerScan, isScanning, onOpenSettings, onOpenTelegramLogs }) {
  return (
    <header className="border-b border-border bg-slate-950/80 backdrop-blur-md sticky top-0 z-50 px-4 sm:px-8 py-4">
      <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        {/* Brand & Title */}
        <div className="flex items-center gap-3.5">
          <div className="w-11 h-11 rounded-xl bg-gradient-to-tr from-sky-500 via-indigo-500 to-violet-600 flex items-center justify-center text-white shadow-lg shadow-sky-500/20 ring-1 ring-white/20">
            <Plane className="w-6 h-6 transform -rotate-45" />
          </div>
          <div>
            <div className="flex items-center gap-2.5">
              <h1 className="text-xl font-extrabold tracking-tight text-white">
                TicketAI
              </h1>
              <span className="text-[11px] font-mono px-2 py-0.5 rounded-md bg-sky-500/10 text-sky-400 border border-sky-500/25 font-semibold flex items-center gap-1">
                <Sparkles className="w-3 h-3 text-sky-400" /> CONSOLE V2
              </span>
            </div>
            <p className="text-xs text-slate-400 font-mono mt-0.5">
              Flight Tracker • Medan (KNO) ➔ Jakarta (CGK) • 17–20 Sept 2026
            </p>
          </div>
        </div>

        {/* Action & Status Controls */}
        <div className="flex flex-wrap items-center gap-2.5 w-full sm:w-auto justify-between sm:justify-end">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-mono">
            <Radio className="w-3.5 h-3.5 animate-pulse text-emerald-400" />
            <span className="font-semibold hidden sm:inline">LIVE 24/7</span>
          </div>

          <button
            onClick={onOpenTelegramLogs}
            title="Telegram Logs & Bot Test Center"
            className="p-2 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-300 hover:text-white border border-slate-800 text-xs font-mono flex items-center gap-1.5 transition-colors cursor-pointer"
          >
            <Send className="w-4 h-4 text-emerald-400" />
            <span className="hidden md:inline">Telegram Log</span>
          </button>

          <button
            onClick={onOpenSettings}
            title="Dashboard Settings"
            className="p-2 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-300 hover:text-white border border-slate-800 text-xs font-mono flex items-center gap-1.5 transition-colors cursor-pointer"
          >
            <Settings className="w-4 h-4 text-sky-400" />
            <span className="hidden md:inline">Settings</span>
          </button>

          <button
            onClick={onTriggerScan}
            disabled={isScanning}
            className={`px-4 py-2 rounded-lg text-xs font-semibold font-mono flex items-center gap-2 transition-all cursor-pointer shadow-lg ${
              isScanning
                ? 'bg-slate-800 text-slate-400 border border-slate-700 cursor-not-allowed'
                : 'bg-gradient-to-r from-sky-500 to-blue-600 hover:from-sky-400 hover:to-blue-500 text-white shadow-sky-500/20 hover:shadow-sky-500/30'
            }`}
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isScanning ? 'animate-spin' : ''}`} />
            {isScanning ? 'Scanning...' : 'Trigger Scan'}
          </button>
        </div>
      </div>
    </header>
  )
}
