# ✈️ TicketAI - Flight Price Tracker & Telegram Notifier

Sistem otomatis pemantau harga tiket pesawat rute **Kualanamu International Airport (KNO - Medan)** menuju **Soekarno-Hatta International Airport (CGK - Jakarta)** pada rentang tanggal **17, 18, dan 19 September 2026**.

Sistem akan memantau penerbangan dan mengirimkan sinyal notifikasi ke **Telegram Bot** Anda ketika tiket pesawat berada di kisaran harga terjangkau (**Rp 1.300.000 s/d Rp 1.599.000** atau lebih murah).

---

## 🛠️ Fitur Utama
- **Pemantauan Otomatis**: Memeriksa harga penerbangan rute KNO -> CGK pada 17-19 September 2026 secara otomatis.
- **Filter Harga Cerdas**: Hanya memberikan sinyal untuk tiket di bawah atau sama dengan Rp 1.599.000.
- **Push Notification Telegram**: Kirim sinyal pesan Telegram yang rapi mencakup Maskapai, Jam Keberangkatan & Kedatangan, Harga, Durasi, dan Link Pemesanan Tiket.
- **Database Anti-Spam (SQLite)**: Menyimpan histori notifikasi sehingga Anda tidak dibombardir oleh pesan yang sama berulang kali. Sinyal baru hanya terkirim saat ada penerbangan murah baru atau harga turun.
- **Scheduler (Daemon Mode)**: Berjalan di latar belakang dengan interval waktu yang dapat disesuaikan (misal: setiap 2 jam).

---

## 🚀 Panduan Memulai (Quick Start)

### 1. Persiapan Token Telegram Bot
1. Buka aplikasi Telegram dan cari `@BotFather`.
2. Kirim pesan `/newbot` dan ikuti petunjuk hingga mendapatkan **HTTP API Token** (contoh: `7123456789:AAFxxx...`).
3. Dapatkan **Chat ID** Telegram Anda dengan mengirimkan pesan ke `@userinfobot` di Telegram.
4. Buka file `.env` di folder ini dan masukkan token serta chat ID Anda:
   ```ini
   TELEGRAM_BOT_TOKEN=7123456789:AAFxxx...
   TELEGRAM_CHAT_ID=123456789
   ```

---

### 2. Menjalankan Aplikasi

#### 🧪 Uji Coba Sinyal Telegram (Test Telegram Connection)
Untuk memastikan Bot Telegram Anda sudah terhubung dan dapat mengirim pesan:
```bash
python main.py --test-telegram
```

#### 🔍 Menjalankan Pemantauan 1 Kali (Run Once)
Untuk memeriksa tiket secara langsung saat ini:
```bash
python main.py --run-once
```

#### 🔄 Menjalankan Pemantauan Otomatis (Daemon / Scheduler Mode)
Untuk menjalankan pemantauan secara terus-menerus di latar belakang (misal setiap 2 jam sekali):
```bash
python main.py --daemon
```

---

## 📂 Struktur Berkas Project

```text
TicketAI/
├── PRD.md              # Product Requirement Document
├── config.py           # Manajemen Konfigurasi (Rute, Tanggal, Threshold, Token)
├── database.py         # SQLite Database Tracker & Anti-Spam Logic
├── notifier.py         # Integrasi Telegram Bot API
├── scraper.py          # Flight Data Search Engine
├── main.py             # Entry Point & APScheduler Runner
├── requirements.txt    # Daftar Dependency Python
├── .env                # File Kredensial & Konfigurasi Lokal
└── .env.example        # Template File Konfigurasi
```
