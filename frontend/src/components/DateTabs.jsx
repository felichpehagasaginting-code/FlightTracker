import React from 'react'
import { Calendar, Tag } from 'lucide-react'
import { formatIDR } from '../lib/utils'

export default function DateTabs({ targetDates, selectedDate, onSelectDate, flights }) {
  // Compute minimum price for each date
  const getMinPriceForDate = (dateStr) => {
    if (!flights || !Array.isArray(flights)) return null
    const list = flights.filter(f => (f.departure_date || f.date) === dateStr)
    if (list.length === 0) return null
    return Math.min(...list.map(f => f.price || 9999999))
  }

  const dates = targetDates || ['2026-09-17', '2026-09-18', '2026-09-19', '2026-09-20']

  return (
    <div className="flex items-center gap-2 overflow-x-auto pb-1 no-scrollbar font-mono text-xs">
      <button
        onClick={() => onSelectDate('all')}
        className={`px-3.5 py-1.5 rounded-lg border font-semibold whitespace-nowrap transition-all cursor-pointer ${
          selectedDate === 'all'
            ? 'bg-sky-500/20 text-sky-400 border-sky-500/40 shadow-sm'
            : 'bg-slate-950 text-slate-400 border-slate-800 hover:text-slate-200'
        }`}
      >
        📅 Semua Tanggal
      </button>

      {dates.map((d) => {
        const minP = getMinPriceForDate(d)
        const isSelected = selectedDate === d
        // Format date string nicely: '2026-09-17' -> '17 Sep'
        const parts = d.split('-')
        const shortDate = parts.length === 3 ? `${parts[2]} Sept` : d

        return (
          <button
            key={d}
            onClick={() => onSelectDate(d)}
            className={`px-3.5 py-1.5 rounded-lg border font-semibold flex items-center gap-2 whitespace-nowrap transition-all cursor-pointer ${
              isSelected
                ? 'bg-sky-500/20 text-sky-400 border-sky-500/40 shadow-sm'
                : 'bg-slate-950 text-slate-400 border-slate-800 hover:text-slate-200'
            }`}
          >
            <span>{shortDate}</span>
            {minP && minP < 9999999 && (
              <span className={`text-[10px] px-2 py-0.5 rounded-md font-bold ${
                minP <= 1599000
                  ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                  : 'bg-slate-800 text-slate-300'
              }`}>
                {formatIDR(minP)}
              </span>
            )}
          </button>
        )
      })}
    </div>
  )
}
