import os
import sys
import threading
import argparse
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

# Handle UTF-8 output on Windows terminal
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write("✅ FlightTracker Bot is running 24/7!".encode("utf-8"))

    def log_message(self, format, *args):
        # Silence HTTP access logs
        return

def start_dashboard_server():
    import uvicorn
    from config import DASHBOARD_PORT
    print(f"🌐 TicketAI Web Dashboard & Health Check running on http://0.0.0.0:{DASHBOARD_PORT}...")
    uvicorn.run("dashboard:app", host="0.0.0.0", port=DASHBOARD_PORT, log_level="warning")


import config
from database import TicketDatabase
from notifier import TelegramNotifier
from scraper import FlightScraper

def evaluate_and_send_alerts(flights=None) -> int:
    """
    Evaluasi daftar penerbangan terhadap threshold harga aktif dan kirim sinyal Telegram.
    Jika flights None, ambil dari 100 data penerbangan terbaru di SQLite.
    """
    db = TicketDatabase()
    notifier = TelegramNotifier()
    
    if flights is None:
        flights = db.get_all_recent_flights(limit=100)

    max_price = config.MAX_AFFORDABLE_PRICE
    min_price = config.MIN_AFFORDABLE_PRICE

    affordable_flights = [
        f for f in flights if f.get("price", 99999999) <= max_price
    ]
    affordable_flights.sort(key=lambda x: x.get("price", 0))

    new_alerts_sent = 0
    for flight in affordable_flights:
        price = flight.get("price", 0)
        formatted_price = f"Rp {price:,.0f}".replace(",", ".")
        if db.should_notify(flight):
            print(f"🚨 Sinyal Baru Adaptif! Mengirim notifikasi Telegram: {flight.get('airline')} [{flight.get('departure_date')}] ({formatted_price})...")
            sent = notifier.send_flight_alert(flight)
            if sent:
                db.record_notification(flight)
                new_alerts_sent += 1
            else:
                print("   ⚠️ Notifikasi Telegram gagal terkirim (cek BOT_TOKEN/CHAT_ID).")
    return new_alerts_sent

def run_flight_check():
    """Eksekusi 1 siklus pemantauan tiket pesawat secara real-time."""
    max_price = config.MAX_AFFORDABLE_PRICE
    min_price = config.MIN_AFFORDABLE_PRICE

    print("=" * 60)
    print(f"⏰ [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Memulai Siklus Pengecekan Tiket Pesawat")
    print(f"📍 Rute: {config.ORIGIN} -> {config.DESTINATION}")
    print(f"📅 Tanggal: {', '.join(config.TARGET_DATES)}")
    print(f"💵 Target Harga Aktif: Rp {min_price:,.0f} - Rp {max_price:,.0f}")
    print("=" * 60)

    db = TicketDatabase()
    scraper = FlightScraper()

    # 1. Scraping data penerbangan live
    all_flights = scraper.search_all_target_dates()
    print(f"📊 Total penerbangan ditemukan: {len(all_flights)} penerbangan.")

    if all_flights:
        db.record_price_snapshots(all_flights)

    # 2. Evaluasi dan kirim sinyal notifikasi Telegram
    new_alerts_sent = evaluate_and_send_alerts(all_flights)

    print("-" * 60)
    print(f"✅ Siklus selesai. {new_alerts_sent} sinyal notifikasi Telegram dikirim.")
    print("=" * 60 + "\n")

def main():
    parser = argparse.ArgumentParser(description="TicketAI - Flight Price Alert & Telegram Bot")
    parser.add_argument("--test-telegram", action="store_true", help="Kirim pesan uji coba ke Telegram Bot")
    parser.add_argument("--run-once", action="store_true", help="Jalankan pemantauan 1 kali lalu selesai")
    parser.add_argument("--daemon", action="store_true", help="Jalankan secara otomatis menggunakan scheduler berkala")
    args = parser.parse_args()

    if args.test_telegram:
        print("🧪 Menguji koneksi & pengiriman sinyal Telegram Bot...")
        notifier = TelegramNotifier()
        if not notifier.is_configured():
            print("❌ TELEGRAM_BOT_TOKEN atau TELEGRAM_CHAT_ID belum diatur di file .env!")
            print("Silakan buka file .env dan isi token bot Telegram Anda terlebih dahulu.")
            sys.exit(1)
        success = notifier.send_test_notification()
        if success:
            print("🎉 Uji coba Telegram sukses! Cek chat Telegram Anda.")
        sys.exit(0 if success else 1)

    if args.daemon:
        from apscheduler.schedulers.blocking import BlockingScheduler
        print(f"🚀 Menjalankan TicketAI dalam Mode Daemon (Setiap {config.CHECK_INTERVAL_MINUTES} menit)...")
        
        # 1. Jalankan FastAPI Web Dashboard & Health Server di background thread
        server_thread = threading.Thread(target=start_dashboard_server, daemon=True)
        server_thread.start()

        # 2. Jalankan Telegram Bot Listener (2-arah) di background thread
        if config.ENABLE_TELEGRAM_BOT_COMMANDS:
            notifier = TelegramNotifier()
            if notifier.is_configured():
                bot_thread = threading.Thread(target=notifier.listen_bot_updates, daemon=True)
                bot_thread.start()

        # 3. Jalankan siklus pemantauan pertama
        run_flight_check()

        # 4. Setup APScheduler berkala (Pemantauan + Daily Digest jam 08:00)
        scheduler = BlockingScheduler()
        scheduler.add_job(run_flight_check, 'interval', minutes=config.CHECK_INTERVAL_MINUTES)
        
        # Daily Digest at 08:00
        digest_hour, digest_minute = config.DAILY_DIGEST_TIME.split(":")
        notifier = TelegramNotifier()
        scheduler.add_job(notifier.send_daily_digest, 'cron', hour=int(digest_hour), minute=int(digest_minute))

        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            print("\n👋 TicketAI Daemon dihentikan.")
            sys.exit(0)
    else:
        # Default run once
        run_flight_check()

if __name__ == "__main__":
    main()
