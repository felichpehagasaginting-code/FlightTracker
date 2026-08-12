import React from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts'
import { TrendingDown, Calendar } from 'lucide-react'
import { formatIDR } from '../lib/utils'

export default function PriceTrendChart({ trends }) {
  // Process trend data array
  // Sample expected trends format: [{ date: '17 Sep', min_price: 1420000, airline: 'Lion Air' }, ...]
  const chartData = (trends || []).map(item => ({
    date: item.date || item.departure_date,
    minPrice: item.min_price || item.lowest_price || item.price,
    airline: item.airline || item.airline_name || 'Multi-Airline',
  }))

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <div className="bg-slate-900 border border-slate-700 p-3 rounded-lg shadow-xl text-xs font-mono">
          <p className="text-slate-300 font-bold flex items-center gap-1.5 border-b border-slate-800 pb-1.5 mb-1.5">
            <Calendar className="w-3.5 h-3.5 text-sky-400" /> {label}
          </p>
          <p className="text-emerald-400 font-semibold text-sm">
            Harga Min: {formatIDR(data.minPrice)}
          </p>
          {data.airline && (
            <p className="text-slate-400 text-[11px] mt-0.5">
              Maskapai: <span className="text-slate-200">{data.airline}</span>
            </p>
          )}
        </div>
      )
    }
    return null
  }

  return (
    <div className="bg-card border border-border rounded-xl p-5 sm:p-6 shadow-sm">
      <div className="flex flex-wrap items-center justify-between gap-4 mb-5">
        <div>
          <h2 className="text-base font-bold text-white flex items-center gap-2">
            <TrendingDown className="w-5 h-5 text-sky-400" /> Price Trend Analytics
          </h2>
          <p className="text-xs text-slate-400 font-mono mt-0.5">
            Harga tiket terendah per tanggal keberangkatan (IDR)
          </p>
        </div>
        <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-sky-500/10 border border-sky-500/20 text-sky-400 text-xs font-mono">
          <span className="w-2 h-2 rounded-full bg-sky-400 animate-pulse"></span>
          Minimum Fare Curve
        </div>
      </div>

      <div className="h-64 w-full">
        {chartData.length > 0 ? (
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData} margin={{ top: 10, right: 20, left: 10, bottom: 0 }}>
              <defs>
                <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#38BDF8" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="#38BDF8" stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
              <XAxis
                dataKey="date"
                stroke="#64748b"
                tick={{ fill: '#94a3b8', fontSize: 12, fontFamily: 'JetBrains Mono' }}
                axisLine={{ stroke: '#334155' }}
              />
              <YAxis
                stroke="#64748b"
                tick={{ fill: '#94a3b8', fontSize: 11, fontFamily: 'JetBrains Mono' }}
                tickFormatter={(val) => `Rp ${(val / 1000).toLocaleString('id-ID')}k`}
                axisLine={{ stroke: '#334155' }}
                domain={['auto', 'auto']}
              />
              <Tooltip content={<CustomTooltip />} />
              <Area
                type="monotone"
                dataKey="minPrice"
                stroke="#38BDF8"
                strokeWidth={3}
                fillOpacity={1}
                fill="url(#priceGradient)"
                dot={{ fill: '#38BDF8', r: 5, strokeWidth: 2, stroke: '#090D16' }}
                activeDot={{ r: 7, fill: '#10B981', stroke: '#ffffff', strokeWidth: 2 }}
              />
            </AreaChart>
          </ResponsiveContainer>
        ) : (
          <div className="h-full flex items-center justify-center text-slate-500 text-xs font-mono border border-dashed border-border rounded-lg">
            Memuat grafik tren harga...
          </div>
        )}
      </div>
    </div>
  )
}
