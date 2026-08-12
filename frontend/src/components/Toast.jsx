import React from 'react'
import { CheckCircle2, AlertCircle, X } from 'lucide-react'

export default function Toast({ toast, onClose }) {
  if (!toast) return null

  const isSuccess = toast.type === 'success'

  return (
    <div className="fixed bottom-6 right-6 z-50 animate-bounce-in max-w-md">
      <div
        className={`p-4 rounded-xl border shadow-2xl flex items-start gap-3 backdrop-blur-lg ${
          isSuccess
            ? 'bg-emerald-950/90 text-emerald-200 border-emerald-500/40 shadow-emerald-950/50'
            : 'bg-rose-950/90 text-rose-200 border-rose-500/40 shadow-rose-950/50'
        }`}
      >
        {isSuccess ? (
          <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
        ) : (
          <AlertCircle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
        )}

        <div className="flex-1 text-xs font-mono">
          <h4 className="font-bold text-white">
            {isSuccess ? 'Scan Pemicu Berhasil' : 'Gagal Picu Scan'}
          </h4>
          <p className="mt-1 opacity-90 leading-relaxed">{toast.message}</p>
        </div>

        <button
          onClick={onClose}
          className="text-slate-400 hover:text-white p-1 rounded-md transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    </div>
  )
}
