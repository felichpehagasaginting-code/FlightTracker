import React, { useState, useMemo } from 'react'
import { Table, Search, ArrowUpDown, ExternalLink, Filter, ShieldAlert, Sparkles, Tag, Eye } from 'lucide-react'
import { formatIDR } from '../lib/utils'
import DateTabs from './DateTabs'

export default function FlightTable({
  flights,
  selectedDate,
  onSelectDate,
  targetDates,
  onSelectFlight,
  maxPriceCap = 1599000
}) {
  const [searchQuery, setSearchQuery] = useState('')
  const [filterMode, setFilterMode] = useState('all') // 'all' | 'target'
  const [sortBy, setSortBy] = useState('price-asc')

  // Filter & sort processing
  const filteredFlights = useMemo(() => {
    let list = Array.isArray(flights) ? [...flights] : []

    // Date Tab Filter
    if (selectedDate && selectedDate !== 'all') {
      list = list.filter(f => (f.departure_date || f.date) === selectedDate)
    }

    // Filter mode (Target <= maxPriceCap)
    if (filterMode === 'target') {
      list = list.filter(f => f.price <= maxPriceCap)
    }

    // Search query
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase()
      list = list.filter(f =>
        (f.airline || '').toLowerCase().includes(q) ||
        (f.departure_date || f.date || '').toLowerCase().includes(q) ||
        (f.departure_time || '').toLowerCase().includes(q)
      )
    }

    // Sorting
    list.sort((a, b) => {
      if (sortBy === 'price-asc') return (a.price || 0) - (b.price || 0)
      if (sortBy === 'price-desc') return (b.price || 0) - (a.price || 0)
      if (sortBy === 'scan-desc') {
        return new Date(b.scanned_at || 0) - new Date(a.scanned_at || 0)
      }
      if (sortBy === 'date-asc') {
        return (a.departure_date || '').localeCompare(b.departure_date || '')
      }
      if (sortBy === 'airline-asc') {
        return (a.airline || '').localeCompare(b.airline || '')
      }
      return 0
    })

    return list
  }, [flights, selectedDate, filterMode, searchQuery, sortBy, maxPriceCap])


  // Helper badge builder
  const renderDealBadge = (price) => {
    if (!price) return null
    if (price < 1300000) {
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-[11px] font-mono font-bold bg-rose-500/15 text-rose-400 border border-rose-500/30 animate-pulse">
          🚨 SUPER CHEAP
        </span>
      )
    }
    if (price <= 1450000) {
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-[11px] font-mono font-semibold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
          🟢 DEAL BAGUS
        </span>
      )
    }
    if (price <= 1599000) {
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-[11px] font-mono font-semibold bg-amber-500/15 text-amber-400 border border-amber-500/30">
          🟡 TARGET MUKRIM
        </span>
      )
    }
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-mono text-slate-400 bg-slate-800/60 border border-slate-700/50">
        ⚪ Standar
      </span>
    )
  }

  return (
    <div className="bg-card border border-border rounded-xl overflow-hidden shadow-sm">
      {/* Date Filter Tabs Bar */}
      <div className="p-4 border-b border-border/80 bg-slate-950/40">
        <DateTabs
          targetDates={targetDates}
          selectedDate={selectedDate}
          onSelectDate={onSelectDate}
          flights={flights}
        />
      </div>

      {/* Header Controls */}
      <div className="p-5 border-b border-border flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-bold text-white flex items-center gap-2">
            <Table className="w-5 h-5 text-sky-400" /> Live Scanned Flights Matrix
          </h2>
          <p className="text-xs text-slate-400 font-mono mt-0.5">
            Menampilkan {filteredFlights.length} dari {flights?.length || 0} tiket yang terpantau (Klik baris untuk detail & link pesan)
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          {/* Sort Dropdown */}
          <div className="flex items-center gap-2 bg-slate-950 px-3 py-1.5 rounded-lg border border-border text-xs font-mono text-slate-300">
            <ArrowUpDown className="w-3.5 h-3.5 text-sky-400" />
            <span className="text-slate-400 text-[11px]">Sort:</span>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="bg-transparent text-white focus:outline-none cursor-pointer font-semibold text-xs"
            >
              <option value="price-asc" className="bg-slate-900 text-slate-200">💵 Harga: Terendah</option>
              <option value="price-desc" className="bg-slate-900 text-slate-200">💵 Harga: Tertinggi</option>
              <option value="scan-desc" className="bg-slate-900 text-slate-200">🕒 Scan: Terbaru</option>
              <option value="date-asc" className="bg-slate-900 text-slate-200">📅 Tanggal: Terawal</option>
              <option value="airline-asc" className="bg-slate-900 text-slate-200">🏢 Maskapai: A ➔ Z</option>
            </select>
          </div>

          {/* Filter Pills */}
          <div className="flex items-center bg-slate-950 p-1 rounded-lg border border-border text-xs font-mono">
            <button
              onClick={() => setFilterMode('all')}
              className={`px-3 py-1 rounded-md font-semibold transition-all ${
                filterMode === 'all'
                  ? 'bg-sky-500/20 text-sky-400 border border-sky-500/30'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Semua Tiket
            </button>
            <button
              onClick={() => setFilterMode('target')}
              className={`px-3 py-1 rounded-md font-semibold transition-all flex items-center gap-1.5 ${
                filterMode === 'target'
                  ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              🎯 Target Sinyal (&le; Rp {Math.round(maxPriceCap / 1000)}k)
            </button>
          </div>

          {/* Search Box */}
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Cari maskapai / tanggal..."
              className="bg-slate-950 border border-border text-xs rounded-lg pl-8 pr-3 py-1.5 text-slate-200 focus:outline-none focus:border-sky-500 w-48 sm:w-56 font-mono"
            />
          </div>
        </div>
      </div>

      {/* Table Content */}
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse text-xs">
          <thead>
            <tr className="bg-slate-950/60 text-slate-400 font-mono uppercase text-[11px] tracking-wider border-b border-border">
              <th className="py-3.5 px-5">Maskapai</th>
              <th className="py-3.5 px-5">Tanggal Keberangkatan</th>
              <th className="py-3.5 px-5">Jam / Durasi</th>
              <th className="py-3.5 px-5">Harga Tiket</th>
              <th className="py-3.5 px-5">Kategori Deal</th>
              <th className="py-3.5 px-5 text-right">Waktu Scan</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border/60">
            {filteredFlights.length > 0 ? (
              filteredFlights.map((flight, idx) => {
                const isAffordable = flight.price <= maxPriceCap
                return (
                  <tr
                    key={flight.id || idx}
                    onClick={() => onSelectFlight && onSelectFlight(flight)}
                    className={`hover:bg-slate-800/60 transition-colors font-mono cursor-pointer group ${
                      isAffordable ? 'bg-emerald-950/10' : ''
                    }`}
                  >
                    {/* Airline */}
                    <td className="py-3.5 px-5 font-semibold text-white flex items-center gap-2">
                      <span className="w-7 h-7 rounded-lg bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300 font-bold text-[10px]">
                        {(flight.airline || 'FL').slice(0, 2).toUpperCase()}
                      </span>
                      <div>
                        <div className="text-slate-100 font-medium">{flight.airline}</div>
                        {flight.flight_number && (
                          <div className="text-[10px] text-slate-400 font-mono">{flight.flight_number}</div>
                        )}
                      </div>
                    </td>

                    {/* Departure Date */}
                    <td className="py-3.5 px-5 text-slate-300">
                      {flight.departure_date || flight.date}
                    </td>

                    {/* Flight Timing */}
                    <td className="py-3.5 px-5 text-slate-300">
                      <div>{flight.departure_time || 'Direct / Langsung'}</div>
                      {flight.duration && (
                        <div className="text-[10px] text-slate-400">{flight.duration}</div>
                      )}
                    </td>

                    {/* Price */}
                    <td className="py-3.5 px-5">
                      <span
                        className={`font-bold text-sm ${
                          isAffordable ? 'text-emerald-400' : 'text-slate-200'
                        }`}
                      >
                        {formatIDR(flight.price)}
                      </span>
                    </td>

                    {/* Deal Badge */}
                    <td className="py-3.5 px-5">
                      {renderDealBadge(flight.price)}
                    </td>

                    {/* Scanned At */}
                    <td className="py-3.5 px-5 text-right text-slate-400 text-[11px]">
                      {flight.scanned_at || 'Terbaru'}
                    </td>
                  </tr>
                )
              })
            ) : (
              <tr>
                <td colSpan={6} className="py-12 text-center text-slate-500 font-mono text-xs">
                  Tidak ada data penerbangan yang sesuai dengan filter.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
