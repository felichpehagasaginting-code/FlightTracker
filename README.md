# ✈️ TicketAI - Automated Flight Tracker, Web Dashboard & Telegram Bot

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Dashboard-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Telegram](https://img.shields.io/badge/Telegram_Bot-2--Way-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)](https://core.telegram.org/bots/api)
[![Playwright](https://img.shields.io/badge/Playwright-Automation-2EAD33?style=for-the-badge&logo=playwright&logoColor=white)](https://playwright.dev/)
[![SQLite](https://img.shields.io/badge/Database-SQLite3-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Render](https://img.shields.io/badge/Deploy-Render.com-46E3B7?style=for-the-badge&logo=render&logoColor=white)](https://render.com/)

**TicketAI** adalah sistem pemantau harga tiket pesawat otomatis **100% data real-time** untuk rute **Kualanamu International Airport (KNO - Medan)** menuju **Soekarno-Hatta International Airport (CGK - Jakarta)** pada rentang tanggal **17, 18, 19, dan 20 September 2026**.

Aplikasi ini dilengkapi dengan **Multi-Provider Scraping Engine**, **Bot Telegram Interaktif 2-Arah**, **Interactive Inline Keyboards**, **Daily Digest Reports**, serta **Visual Web Dashboard UI** bertema *OLED Dark Mode* berbasis FastAPI & Chart.js.

---

## 🖥️ Web Dashboard Operations Console (`http://127.0.0.1:10000/`)

![TicketAI Operations Console](assets/dashboard_preview.png)

Dashboard web interaktif otomatis aktif di port `10000` saat aplikasi dijalankan dalam mode `--daemon`:

- **Stat Cards**: Menampilkan jumlah scan executed (`740+`), sinyal terkirim, harga terendah recorded (`Rp 1.647.550`), dan total penerbangan unik (`124`).
- **Price Trend Analytics Chart**: Grafik garis interaktif tren harga terendah per tanggal keberangkatan berbasis Chart.js.
- **Interactive Sort By Control**: Pengurutan tabel instan berdasarkan *Harga Terendah*, *Harga Tertinggi*, *Waktu Scan Terbaru*, *Tanggal Terawal*, atau *Nama Maskapai (A-Z)*.
- **Live Scanned Flights Matrix**: Tabel 124+ penerbangan real-time (Garuda Indonesia, Batik Air, Super Air Jet, Citilink, AirAsia) dengan pencarian maskapai & tombol filter pill `[Semua Tiket]` vs `[🎯 Target Sinyal (<= Rp 1.599k)]`.
- **Trigger Manual Scan Button**: Tombol manual untuk memicu pengecekan tiket instan dari browser.

---

## 📱 Cara Mengakses Web Dashboard dari HP (Mobile Device)

### Cara 1: Menggunakan Wi-Fi / Hotspot Lokal
1. Pastikan **HP dan Laptop terhubung ke jaringan Wi-Fi / Hotspot yang sama**.
2. Alamat IP Laptop Anda saat ini: **`192.168.1.4`**
3. Buka browser di HP Anda (Chrome, Safari, dll), lalu ketik alamat:
   👉 **`http://192.168.1.4:10000/`**

### Cara 2: Akses Global via Cloud (Render.com)
1. Buka URL Web Service Render Anda di browser HP (dapat diakses dari mana saja via 4G/5G/Wi-Fi):
   👉 **`https://ticketai-flight-tracker.onrender.com/`**

---

## 🌟 Fitur Utama (Core Features)

- ⚡ **Multi-Provider Scraper Engine**: Pengambilan data *live* real-time dari Google Flights menggunakan Playwright Chromium dengan **HTTP Fallback Scraper** otomatis.
- 💯 **100% Real-Time Data (No Mock Data)**: Seluruh data penerbangan dan statistik di-extract murni secara *live* dari penyedia penerbangan tanpa data palsu/sample.
- 📅 **Multi-Date Tracking**: Pemantauan 4 tanggal target: **17, 18, 19, & 20 September 2026** (configurable via `.env`).
- 🤖 **Bot Telegram Interaktif 2-Arah**:
  - `/check` — Menjalankan pengecekan tiket instan kapan saja dari chat Telegram.
  - `/status` — Melihat ringkasan statistik scan dan status bot.
  - `/dates` — Melihat daftar tanggal target aktif.
  - `/help` — Menampilkan bantuan perintah bot.
- 🔘 **Telegram Inline Keyboard Buttons**:
  - `[🎫 Pesan Tiket Sekarang]` — Deep-link langsung ke pemesanan tiket.
  - `[🔕 Mute Penerbangan Ini]` — Hentikan alert berulang untuk penerbangan tertentu.
- 📊 **Daily Digest Report**: Laporan ringkasan harian otomatis setiap jam 08:00 pagi WIB mencakup harga rata-rata dan 5 tiket termurah 24 jam terakhir.
- 🎨 **Local SVG Vector Stickers**: Pengiriman stiker vektor `.svg` (`super_cheap.svg`, `good_deal.svg`, `affordable.svg`) yang disesuaikan dengan kategori deal harga.
- 🛡️ **Anti-Spam SQLite Engine**: Mencegah spam pesan berulang untuk tiket & harga yang sama, namun tetap alert saat terjadi penurunan harga.

---

## 🏗️ Arsitektur Sistem

```mermaid
graph TD
    A[APScheduler / Daemon] -->|Interval 30m / Daily 08:00| B[Multi-Provider FlightScraper]
    B -->|1st Try: Playwright Chromium| C[Google Flights Live Data]
    B -->|Fallback: HTTP Engine| C
    C --> D[SQLite History Database - price_history]
    D --> E{Price Filter & Anti-Spam Check}
    E -->|Above Cap / Muted / Same Price| F[Skip Notification]
    E -->|New Ticket / Price Drop| G[Telegram Notifier API]
    G -->|Send SVG Sticker & Inline Buttons| H[User Telegram Chat]
    I[Telegram Bot Listener 2-Way] -->|Listen /check /status /mute| D
    J[FastAPI Web Server :10000] -->|Serve UI & JSON APIs| K[Visual Web Dashboard - Chart.js]
```

---

## 💬 Preview Notifikasi Telegram & Inline Buttons

```text
🎨 [Stiker Vektor SVG Terkirim]

✈️ SINYAL TIKET PESAWAT MURAH!
Status: 🟢 DEAL BAGUS BANGET
Tipe: Sekali Jalan (One-Way)

📍 Rute: Medan (KNO) ➡️ Jakarta (CGK)
📅 Tanggal: 2026-09-18
💵 Harga: Rp 1.420.000

🏢 Maskapai: Batik Air (ID-6881)
🕒 Waktu: 08:30 - 10:50 (Direct)
⏱️ Durasi: 2j 20m
-------------------------------------------
🤖 TicketAI Automated Tracker

[ 🎫 Pesan Tiket Sekarang ] [ 🔕 Mute Penerbangan Ini ]
```

---

## 🚀 Panduan Penggunaan (Quick Start)

### 1. Prasyarat System
- Python 3.10 atau versi yang lebih baru
- Node.js (untuk Playwright Chromium browser)

### 2. Instalasi & Setup

```bash
# 1. Clone repository ini
git clone https://github.com/felichpehagasaginting-code/FlightTracker.git
cd TicketAI

# 2. Buat & aktifkan virtual environment (opsional)
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 3. Install dependencies Python
pip install -r requirements.txt

# 4. Install Playwright Chromium Browser
playwright install chromium
```

### 3. Konfigurasi `.env`

Salin file template `.env.example` menjadi `.env`:

```bash
cp .env.example .env
```

Isi kredensial Telegram Bot Anda di file `.env`:

```ini
# Parameter Pemantauan Tiket
FLIGHT_ORIGIN=KNO
FLIGHT_DESTINATION=CGK
FLIGHT_TARGET_DATES=2026-09-17,2026-09-18,2026-09-19,2026-09-20

# Threshold Harga (IDR)
MIN_AFFORDABLE_PRICE=1300000
MAX_AFFORDABLE_PRICE=1599000

# Telegram Bot API Credentials & Stiker SVG
TELEGRAM_BOT_TOKEN=7123456789:AAFxxxxxxxxxxxxxxxxxxxx
TELEGRAM_CHAT_ID=123456789
ENABLE_SVG_STICKERS=true
ENABLE_TELEGRAM_BOT_COMMANDS=true

# Interval Penjadwalan & Server Port
CHECK_INTERVAL_MINUTES=30
PORT=10000
DAILY_DIGEST_TIME=08:00
```

---

## ⚙️ Perintah CLI (Command Line Interface)

#### 🧪 1. Uji Coba Telegram & Stiker SVG
```bash
python main.py --test-telegram
```

#### 🔍 2. Menjalankan Pemantauan 1 Kali (Run Once)
```bash
python main.py --run-once
```

#### 🔄 3. Menjalankan Mode Otomatis 24/7 (Daemon Mode & Web Dashboard)
```bash
python main.py --daemon
```

---

## 📊 Tabel Parameter Konfigurasi (`.env`)

| Variable | Default Value | Deskripsi |
| :--- | :--- | :--- |
| `FLIGHT_ORIGIN` | `KNO` | Kode IATA bandara keberangkatan |
| `FLIGHT_DESTINATION` | `CGK` | Kode IATA bandara tujuan |
| `FLIGHT_TARGET_DATES` | `2026-09-17,...,2026-09-20` | Tanggal target penerbangan (koma) |
| `MIN_AFFORDABLE_PRICE` | `1300000` | Batas bawah harga deal (IDR) |
| `MAX_AFFORDABLE_PRICE` | `1599000` | Batas atas harga toleransi (IDR) |
| `TELEGRAM_BOT_TOKEN` | *Wajib* | Token HTTP API Telegram Bot |
| `TELEGRAM_CHAT_ID` | *Auto-discover* | Chat ID penerima notifikasi |
| `ENABLE_SVG_STICKERS` | `true` | Kirim stiker ilustrasi SVG lokal |
| `ENABLE_TELEGRAM_BOT_COMMANDS` | `true` | Aktifkan listener bot 2-arah (`/check`, `/status`) |
| `CHECK_INTERVAL_MINUTES`| `30` | Interval pengecekan berkala (menit) |
| `PORT` | `10000` | Port server FastAPI Dashboard & Health Check |
| `DAILY_DIGEST_TIME` | `08:00` | Jam pengiriman laporan harian (WIB) |

---

## 🌐 Deploy 24/7 Gratis ke Cloud (Render.com)

Aplikasi ini dilengkapi `Dockerfile`, `render.yaml`, dan **FastAPI Server** internal (port 10000) untuk deploy gratis di **Render.com**:

1. Push repository ke GitHub.
2. Buat **New Web Service** di [Render.com](https://render.com/).
3. Hubungkan repository GitHub Anda.
4. Set Environment Variables di Render Dashboard (`TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`).
5. Render akan secara otomatis menjalankan TicketAI 24/7!

---

## 📂 Struktur Berkas Project

```text
TicketAI/
├── assets/
│   ├── stickers/       # Asset Stiker Vektor SVG (super_cheap.svg, good_deal.svg, dll)
│   └── dashboard_preview.png # Screenshot Tangkapan Layar Web Dashboard
├── templates/
│   └── index.html      # Visual Web Dashboard UI (FastAPI + Tailwind + Chart.js)
├── PRD.md              # Product Requirement Document & Spesifikasi Sistem
├── README.md           # Dokumentasi Resmi Project
├── Dockerfile          # Containerization Blueprint (Playwright & Python 3.10)
├── render.yaml         # Blueprint Cloud Deployment (Render.com)
├── dashboard.py        # FastAPI Server & JSON API Endpoints
├── config.py           # Central Configuration Manager
├── database.py         # SQLite Storage Engine & Price History Analytics
├── notifier.py         # Telegram Bot API Notifier (Messages, SVG Stickers, 2-Way Bot)
├── scraper.py          # Multi-Provider Real-Time Data Engine (Playwright + HTTP Fallback)
├── main.py             # Application Entry Point & APScheduler Daemon
├── requirements.txt    # Daftar Python Dependencies
├── .env                # File Environment & Kredensial Lokal
└── .env.example        # Template File Environment
```

---

## 📜 Lisensi
Project ini dibuat di bawah lisensi MIT.
