import React, { useState } from 'react'
import { X, Settings, Save, Sliders, CheckCircle2, AlertCircle } from 'lucide-react'
import { formatIDR } from '../lib/utils'

export default function SettingsModal({ settings, onClose, onSave }) {
  const [maxPriceCap, setMaxPriceCap] = useState(settings?.max_price_cap || 1599000)
  const [minPriceTarget, setMinPriceTarget] = useState(settings?.min_price_target || 1300000)
  const [checkInterval, setCheckInterval] = useState(settings?.check_interval_min || 30)
  const [isSaving, setIsSaving] = useState(false)

  const handleSave = async () => {
    setIsSaving(true)
    await onSave({
      max_price_cap: maxPriceCap,
      min_price_target: minPriceTarget,
      check_interval_min: checkInterval
    })
    setIsSaving(false)
    onClose()
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-fade-in">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full overflow-hidden shadow-2xl">
        {/* Header */}
        <div className="bg-slate-950 p-5 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-sky-500/10 text-sky-400 border border-sky-500/20">
              <Settings className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">Dashboard Settings</h3>
              <p className="text-xs text-slate-400 font-mono">Konfigurasi Target Price & Scheduler</p>
            </div>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white p-1 rounded-lg">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form Body */}
        <div className="p-6 space-y-5 font-mono text-xs">
          {/* Max Price Cap Slider */}
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <label className="text-slate-300 font-semibold">Max Price Cap Target</label>
              <span className="text-amber-400 font-bold text-sm">{formatIDR(maxPriceCap)}</span>
            </div>
            <input
              type="range"
              min="1000000"
              max="3000000"
              step="50000"
              value={maxPriceCap}
              onChange={(e) => setMaxPriceCap(Number(e.target.value))}
              className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-sky-400"
            />
            <p className="text-[10px] text-slate-500">Tiket di bawah harga ini akan dianggap sebagai "Affordable Target".</p>
          </div>

          {/* Min Price Target */}
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <label className="text-slate-300 font-semibold">Min Price Deal Threshold</label>
              <span className="text-emerald-400 font-bold text-sm">{formatIDR(minPriceTarget)}</span>
            </div>
            <input
              type="range"
              min="800000"
              max="2000000"
              step="50000"
              value={minPriceTarget}
              onChange={(e) => setMinPriceTarget(Number(e.target.value))}
              className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-emerald-400"
            />
            <p className="text-[10px] text-slate-500">Tiket di bawah harga ini akan ditandai sebagai "Super Cheap Deal".</p>
          </div>

          {/* Check Interval */}
          <div className="space-y-2">
            <label className="text-slate-300 font-semibold block">Interval Scan Otomatis</label>
            <div className="grid grid-cols-4 gap-2">
              {[15, 30, 60, 120].map((mins) => (
                <button
                  key={mins}
                  type="button"
                  onClick={() => setCheckInterval(mins)}
                  className={`py-2 rounded-lg text-center font-bold border transition-all ${
                    checkInterval === mins
                      ? 'bg-sky-500/20 text-sky-400 border-sky-500/40'
                      : 'bg-slate-950 text-slate-400 border-slate-800 hover:text-slate-200'
                  }`}
                >
                  {mins}m
                </button>
              ))}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="pt-4 border-t border-slate-800 flex items-center justify-end gap-3">
            <button
              onClick={onClose}
              className="px-4 py-2 rounded-lg text-slate-400 hover:text-white bg-slate-800/60"
            >
              Batal
            </button>
            <button
              onClick={handleSave}
              disabled={isSaving}
              className="px-5 py-2 rounded-lg bg-sky-500 hover:bg-sky-400 text-slate-950 font-bold flex items-center gap-2 cursor-pointer shadow-lg shadow-sky-500/20"
            >
              <Save className="w-4 h-4" /> {isSaving ? 'Menyimpan...' : 'Simpan Pengaturan'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
