import React from 'react'
import { X, ExternalLink, Plane, Clock, Calendar, ShieldCheck, Tag, Sparkles, MapPin } from 'lucide-react'
import { formatIDR } from '../lib/utils'

export default function FlightDetailModal({ flight, onClose, maxPriceCap }) {
  if (!flight) return null

  const isAffordable = flight.price <= (maxPriceCap || 1599000)

  const getDealBadgeInfo = (price) => {
    if (price < 1300000) {
      return { label: 'SUPER CHEAP', color: 'bg-rose-500/20 text-rose-400 border-rose-500/40', icon: '🚨' }
    }
    if (price <= 1450000) {
      return { label: 'DEAL BAGUS', color: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40', icon: '🟢' }
    }
    if (price <= (maxPriceCap || 1599000)) {
      return { label: 'TARGET MUKRIM', color: 'bg-amber-500/20 text-amber-400 border-amber-500/40', icon: '🟡' }
    }
    return { label: 'Harga Standar', color: 'bg-slate-800 text-slate-400 border-slate-700', icon: '⚪' }
  }

  const badge = getDealBadgeInfo(flight.price)
  const bookingUrl = flight.booking_link || `https://www.google.com/travel/flights?q=Flights+from+KNO+to+CGK+on+${flight.departure_date || flight.date}`

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-fade-in">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full overflow-hidden shadow-2xl relative">
        {/* Header Banner */}
        <div className="bg-gradient-to-r from-slate-950 via-slate-900 to-sky-950 p-6 border-b border-slate-800 flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-sky-500/10 border border-sky-500/25 flex items-center justify-center text-sky-400 font-bold text-lg">
              <Plane className="w-6 h-6 transform -rotate-45" />
            </div>
            <div>
              <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold border mb-1 ${badge.color}`}>
                {badge.icon} {badge.label}
              </span>
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                {flight.airline}
              </h3>
              <p className="text-xs text-slate-400 font-mono">
                {flight.flight_number ? `Flight ${flight.flight_number}` : 'Penerbangan Langsung'}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white p-1.5 rounded-lg bg-slate-800/50 hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 space-y-6">
          {/* Route Overview */}
          <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-4 flex items-center justify-between">
            <div className="text-center sm:text-left">
              <p className="text-[10px] font-mono uppercase text-slate-500">Keberangkatan</p>
              <h4 className="text-base font-bold text-white">Medan (KNO)</h4>
              <p className="text-xs font-mono text-sky-400 mt-0.5">{flight.departure_time || '08:30 WIB'}</p>
            </div>

            <div className="flex flex-col items-center px-4">
              <span className="text-[10px] font-mono text-slate-500">{flight.duration || '2j 20m'}</span>
              <div className="w-20 sm:w-28 h-0.5 bg-sky-500/30 my-1 relative">
                <Plane className="w-3.5 h-3.5 text-sky-400 absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2" />
              </div>
              <span className="text-[9px] font-mono text-emerald-400">Direct Flight</span>
            </div>

            <div className="text-center sm:text-right">
              <p className="text-[10px] font-mono uppercase text-slate-500">Kedatangan</p>
              <h4 className="text-base font-bold text-white">Jakarta (CGK)</h4>
              <p className="text-xs font-mono text-sky-400 mt-0.5">{flight.arrival_time || '10:50 WIB'}</p>
            </div>
          </div>

          {/* Key Flight Metrics */}
          <div className="grid grid-cols-2 gap-3 font-mono text-xs">
            <div className="bg-slate-950/40 p-3 rounded-lg border border-slate-800/60">
              <span className="text-slate-500 block text-[10px]">TANGGAL KEBERANGKATAN</span>
              <span className="text-slate-200 font-semibold flex items-center gap-1.5 mt-1">
                <Calendar className="w-3.5 h-3.5 text-sky-400" /> {flight.departure_date || flight.date}
              </span>
            </div>
            <div className="bg-slate-950/40 p-3 rounded-lg border border-slate-800/60">
              <span className="text-slate-500 block text-[10px]">HARGA TERDETEKSI</span>
              <span className={`text-base font-bold mt-0.5 block ${isAffordable ? 'text-emerald-400' : 'text-slate-200'}`}>
                {formatIDR(flight.price)}
              </span>
            </div>
          </div>

          {/* Booking CTA Button */}
          <a
            href={bookingUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="w-full py-3.5 px-5 rounded-xl font-mono text-xs font-bold bg-gradient-to-r from-sky-500 via-blue-600 to-indigo-600 hover:from-sky-400 hover:to-indigo-500 text-white shadow-lg shadow-sky-500/25 flex items-center justify-center gap-2 transition-all cursor-pointer"
          >
            <ExternalLink className="w-4 h-4" /> Pesan Tiket Sekarang (Google Flights)
          </a>
        </div>
      </div>
    </div>
  )
}
