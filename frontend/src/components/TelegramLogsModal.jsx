import React, { useState } from 'react'
import { X, Send, Bell, ShieldCheck, ExternalLink, CheckCircle2, Radio, Terminal } from 'lucide-react'
import { formatIDR } from '../lib/utils'

export default function TelegramLogsModal({ logs, onClose, onSendTestSignal }) {
  const [isSending, setIsSending] = useState(false)

  const handleTestSignal = async () => {
    setIsSending(true)
    await onSendTestSignal()
    setIsSending(false)
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-fade-in">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-2xl w-full overflow-hidden shadow-2xl">
        {/* Header */}
        <div className="bg-slate-950 p-5 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <Send className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                Telegram Activity Log & Test Center
              </h3>
              <p className="text-xs text-slate-400 font-mono">Riwayat Sinyal & Pengujian Koneksi Telegram Bot</p>
            </div>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white p-1 rounded-lg">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 space-y-5">
          {/* Bot Connectivity Test Banner */}
          <div className="bg-gradient-to-r from-emerald-950/40 to-slate-950 border border-emerald-500/30 rounded-xl p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div>
              <span className="text-xs font-mono font-bold text-emerald-400 flex items-center gap-1.5">
                <Radio className="w-3.5 h-3.5 animate-pulse" /> Telegram Bot Active
              </span>
              <p className="text-xs text-slate-400 mt-0.5 font-mono">Uji pengiriman notifikasi langsung ke HP Anda.</p>
            </div>
            <button
              onClick={handleTestSignal}
              disabled={isSending}
              className={`px-4 py-2 rounded-lg text-xs font-mono font-bold flex items-center gap-2 transition-all cursor-pointer shadow-lg ${
                isSending
                  ? 'bg-slate-800 text-slate-500 border border-slate-700'
                  : 'bg-emerald-500 hover:bg-emerald-400 text-slate-950 shadow-emerald-500/20'
              }`}
            >
              <Send className={`w-3.5 h-3.5 ${isSending ? 'animate-spin' : ''}`} />
              {isSending ? 'Sending Test...' : 'Send Test Signal 🚀'}
            </button>
          </div>

          {/* Logs Table */}
          <div className="space-y-2">
            <h4 className="text-xs font-mono font-semibold text-slate-300 flex items-center gap-1.5 uppercase">
              <Terminal className="w-3.5 h-3.5 text-sky-400" /> Riwayat Sinyal Terkirim (Anti-Spam Storage)
            </h4>

            <div className="bg-slate-950 border border-slate-800 rounded-xl overflow-hidden max-h-64 overflow-y-auto">
              {logs && logs.length > 0 ? (
                <div className="divide-y divide-slate-800/60 font-mono text-xs">
                  {logs.map((log, idx) => (
                    <div key={log.id || idx} className="p-3.5 hover:bg-slate-900/60 transition-colors flex items-center justify-between gap-4">
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-white">{log.airline}</span>
                          <span className="text-[10px] text-slate-400">{log.flight_number || ''}</span>
                        </div>
                        <p className="text-[11px] text-slate-400 mt-0.5">
                          {log.departure_date} • {log.departure_time || '08:30'} ➔ {log.arrival_time || '10:50'}
                        </p>
                      </div>

                      <div className="text-right">
                        <span className="text-emerald-400 font-bold text-sm block">
                          {formatIDR(log.price)}
                        </span>
                        <span className="text-[10px] text-slate-500 block mt-0.5">
                          {log.notified_at || 'Terbaru'}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="p-8 text-center text-slate-500 font-mono text-xs">
                  Belum ada sinyal notifikasi Telegram yang tercatat.
                </div>
              )}
            </div>
          </div>

          <div className="pt-2 border-t border-slate-800 flex justify-end">
            <button
              onClick={onClose}
              className="px-4 py-2 rounded-lg text-xs font-mono bg-slate-800 text-slate-300 hover:text-white"
            >
              Tutup
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
