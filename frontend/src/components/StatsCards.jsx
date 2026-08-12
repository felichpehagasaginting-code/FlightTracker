import React from 'react'
import { Activity, Bell, TrendingDown, Layers, ShieldCheck } from 'lucide-react'
import { formatIDR } from '../lib/utils'

export default function StatsCards({ stats, priceCap, intervalMin }) {
  const scansCount = stats?.total_scans ?? stats?.total_scans_executed ?? 0
  const alertsCount = stats?.total_alerts_sent ?? stats?.signals_sent ?? 0
  const lowestPrice = stats?.lowest_price_recorded ?? stats?.lowest_price ?? null
  const uniqueFlights = stats?.unique_flights_count ?? stats?.unique_flights ?? 0

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {/* Total Scans */}
      <div className="bg-card border border-border rounded-xl p-5 relative overflow-hidden shadow-sm hover:border-slate-700 transition-colors">
        <div className="flex justify-between items-start">
          <div>
            <p className="text-xs font-mono text-slate-400 uppercase tracking-wider">Total Scans Executed</p>
            <h3 className="text-3xl font-mono font-bold text-white mt-1.5">{scansCount}</h3>
          </div>
          <div className="p-2.5 rounded-lg bg-sky-500/10 text-sky-400 border border-sky-500/20">
            <Activity className="w-5 h-5" />
          </div>
        </div>
        <div className="mt-3 flex items-center justify-between text-xs font-mono border-t border-border/50 pt-2.5">
          <span className="text-slate-400">Interval</span>
          <span className="text-sky-400 font-semibold">{intervalMin ? `${intervalMin} menit` : '30 menit'}</span>
        </div>
      </div>

      {/* Signals Sent */}
      <div className="bg-card border border-border rounded-xl p-5 relative overflow-hidden shadow-sm hover:border-slate-700 transition-colors">
        <div className="flex justify-between items-start">
          <div>
            <p className="text-xs font-mono text-slate-400 uppercase tracking-wider">Telegram Signals Sent</p>
            <h3 className="text-3xl font-mono font-bold text-emerald-400 mt-1.5">{alertsCount}</h3>
          </div>
          <div className="p-2.5 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <Bell className="w-5 h-5" />
          </div>
        </div>
        <div className="mt-3 flex items-center justify-between text-xs font-mono border-t border-border/50 pt-2.5">
          <span className="text-slate-400 flex items-center gap-1">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" /> Anti-Spam Filter
          </span>
          <span className="text-emerald-400 font-semibold">ACTIVE</span>
        </div>
      </div>

      {/* Lowest Price Recorded */}
      <div className="bg-card border border-emerald-500/30 rounded-xl p-5 relative overflow-hidden shadow-glow-emerald">
        <div className="flex justify-between items-start">
          <div>
            <p className="text-xs font-mono text-slate-400 uppercase tracking-wider">Lowest Price Found</p>
            <h3 className="text-2xl font-mono font-bold text-emerald-400 mt-1.5">
              {lowestPrice ? formatIDR(lowestPrice) : '-'}
            </h3>
          </div>
          <div className="p-2.5 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <TrendingDown className="w-5 h-5" />
          </div>
        </div>
        <div className="mt-3 flex items-center justify-between text-xs font-mono border-t border-border/50 pt-2.5">
          <span className="text-slate-400">Price Cap Target</span>
          <span className="text-amber-400 font-semibold">{formatIDR(priceCap || 1599000)}</span>
        </div>
      </div>

      {/* Unique Flights Monitored */}
      <div className="bg-card border border-border rounded-xl p-5 relative overflow-hidden shadow-sm hover:border-slate-700 transition-colors">
        <div className="flex justify-between items-start">
          <div>
            <p className="text-xs font-mono text-slate-400 uppercase tracking-wider">Unique Flights Monitored</p>
            <h3 className="text-3xl font-mono font-bold text-sky-400 mt-1.5">{uniqueFlights}</h3>
          </div>
          <div className="p-2.5 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
            <Layers className="w-5 h-5" />
          </div>
        </div>
        <div className="mt-3 flex items-center justify-between text-xs font-mono border-t border-border/50 pt-2.5">
          <span className="text-slate-400">Target Range</span>
          <span className="text-slate-200 font-semibold">17–20 Sept 2026</span>
        </div>
      </div>
    </div>
  )
}
