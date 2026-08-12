import React, { useState, useEffect, useCallback } from 'react'
import Header from './components/Header'
import StatsCards from './components/StatsCards'
import PriceTrendChart from './components/PriceTrendChart'
import FlightTable from './components/FlightTable'
import FlightDetailModal from './components/FlightDetailModal'
import SettingsModal from './components/SettingsModal'
import TelegramLogsModal from './components/TelegramLogsModal'
import Toast from './components/Toast'

export default function App() {
  const [statsData, setStatsData] = useState(null)
  const [flights, setFlights] = useState([])
  const [trends, setTrends] = useState([])
  const [settings, setSettings] = useState(null)
  const [telegramLogs, setTelegramLogs] = useState([])

  const [selectedDate, setSelectedDate] = useState('all')
  const [selectedFlight, setSelectedFlight] = useState(null)
  const [showSettings, setShowSettings] = useState(false)
  const [showTelegramLogs, setShowTelegramLogs] = useState(false)

  const [isScanning, setIsScanning] = useState(false)
  const [toast, setToast] = useState(null)
  const [lastUpdated, setLastUpdated] = useState(null)

  // Fetch helper with fallback to port 10000 if proxy isn't available
  const apiFetch = async (endpoint, options = {}) => {
    try {
      let res = await fetch(endpoint, options)
      if (res.ok) return res
      res = await fetch(`http://localhost:10000${endpoint}`, options)
      return res
    } catch {
      return fetch(`http://localhost:10000${endpoint}`, options)
    }
  }

  // Fetch all dashboard data from FastAPI
  const fetchDashboardData = useCallback(async () => {
    try {
      const [resStats, resFlights, resTrends, resSettings] = await Promise.all([
        apiFetch('/api/stats'),
        apiFetch('/api/flights?limit=100'),
        apiFetch('/api/trends'),
        apiFetch('/api/settings')
      ])

      if (resStats && resStats.ok) {
        const data = await resStats.json()
        setStatsData(data)
      }

      if (resFlights && resFlights.ok) {
        const data = await resFlights.json()
        setFlights(data)
      }

      if (resTrends && resTrends.ok) {
        const data = await resTrends.json()
        setTrends(data)
      }

      if (resSettings && resSettings.ok) {
        const data = await resSettings.json()
        setSettings(data)
      }

      setLastUpdated(new Date())
    } catch (err) {
      console.error('Error fetching dashboard data:', err)
    }
  }, [])

  // Fetch Telegram logs when modal opens
  const fetchTelegramLogs = async () => {
    try {
      const res = await apiFetch('/api/telegram/logs')
      if (res && res.ok) {
        const data = await res.json()
        setTelegramLogs(data)
      }
    } catch (err) {
      console.error('Error fetching Telegram logs:', err)
    }
  }

  // Initial load & periodic polling
  useEffect(() => {
    fetchDashboardData()
    const interval = setInterval(fetchDashboardData, 10000)
    return () => clearInterval(interval)
  }, [fetchDashboardData])

  // Trigger manual flight check
  const handleTriggerScan = async () => {
    setIsScanning(true)
    try {
      const res = await apiFetch('/api/trigger-check', { method: 'POST' })
      const data = await res.json()
      if (res && res.ok) {
        setToast({ type: 'success', message: data.message || 'Proses pengecekan tiket manual berhasil dipicu!' })
        setTimeout(fetchDashboardData, 2000)
      } else {
        setToast({ type: 'error', message: data.message || 'Gagal memicu pengecekan tiket manual.' })
      }
    } catch (err) {
      setToast({ type: 'error', message: `Gagal terhubung ke backend server: ${err.message}` })
    } fontally: {
      setIsScanning(false)
    }
  }

  // Save Settings handler
  const handleSaveSettings = async (newSettings) => {
    try {
      const res = await apiFetch('/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newSettings)
      })
      const data = await res.json()
      if (res && res.ok) {
        setToast({ type: 'success', message: 'Pengaturan threshold harga & interval berhasil disimpan!' })
        fetchDashboardData()
      } else {
        setToast({ type: 'error', message: data.message || 'Gagal menyimpan pengaturan.' })
      }
    } catch (err) {
      setToast({ type: 'error', message: `Gagal menyimpan pengaturan: ${err.message}` })
    }
  }

  // Send Test Telegram Signal handler
  const handleSendTestSignal = async () => {
    try {
      const res = await apiFetch('/api/telegram/test', { method: 'POST' })
      const data = await res.json()
      if (res && res.ok) {
        setToast({ type: 'success', message: '🟢 Sinyal uji coba Telegram berhasil terkirim ke bot Anda!' })
        fetchTelegramLogs()
      } else {
        setToast({ type: 'error', message: data.message || 'Gagal mengirim sinyal Telegram test.' })
      }
    } catch (err) {
      setToast({ type: 'error', message: `Error pengujian Telegram: ${err.message}` })
    }
  }

  const handleOpenTelegramLogs = () => {
    fetchTelegramLogs()
    setShowTelegramLogs(true)
  }

  return (
    <div className="min-h-screen bg-oled text-slate-100 flex flex-col antialiased selection:bg-sky-500 selection:text-white">
      {/* Top Header Navigation */}
      <Header
        onTriggerScan={handleTriggerScan}
        isScanning={isScanning}
        onOpenSettings={() => setShowSettings(true)}
        onOpenTelegramLogs={handleOpenTelegramLogs}
      />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 md:p-8 space-y-6">
        {/* Metric Cards Grid */}
        <StatsCards
          stats={statsData?.stats}
          priceCap={settings?.max_price_cap || statsData?.price_cap}
          intervalMin={settings?.check_interval_min || statsData?.check_interval_min}
        />

        {/* Price Trend Chart Section */}
        <PriceTrendChart trends={trends} />

        {/* Live Scanned Flights Matrix Table */}
        <FlightTable
          flights={flights}
          selectedDate={selectedDate}
          onSelectDate={setSelectedDate}
          targetDates={statsData?.target_dates}
          onSelectFlight={setSelectedFlight}
          maxPriceCap={settings?.max_price_cap || 1599000}
        />
      </main>

      {/* Footer */}
      <footer className="border-t border-border py-6 text-center text-xs font-mono text-slate-500">
        <p>TicketAI Monitoring Console • Powered by FastAPI & React shadcn/ui</p>
      </footer>

      {/* Flight Detail Modal */}
      {selectedFlight && (
        <FlightDetailModal
          flight={selectedFlight}
          onClose={() => setSelectedFlight(null)}
          maxPriceCap={settings?.max_price_cap || 1599000}
        />
      )}

      {/* Settings Modal */}
      {showSettings && (
        <SettingsModal
          settings={settings}
          onClose={() => setShowSettings(false)}
          onSave={handleSaveSettings}
        />
      )}

      {/* Telegram Logs & Test Center Modal */}
      {showTelegramLogs && (
        <TelegramLogsModal
          logs={telegramLogs}
          onClose={() => setShowTelegramLogs(false)}
          onSendTestSignal={handleSendTestSignal}
        />
      )}

      {/* Toast Alert */}
      <Toast toast={toast} onClose={() => setToast(null)} />
    </div>
  )
}
