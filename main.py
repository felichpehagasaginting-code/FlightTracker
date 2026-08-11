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

def start_health_check_server():
    port = int(os.getenv("PORT", "10000"))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    print(f"🌐 Health check server listening on port {port}...")
    server.serve_forever()


from config import (
    ORIGIN, DESTINATION, TARGET_DATES, 
    MIN_AFFORDABLE_PRICE, MAX_AFFORDABLE_PRICE, 
    CHECK_INTERVAL_MINUTES, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
)
from database import TicketDatabase
from notifier import TelegramNotifier
from scraper import FlightScraper

def run_flight_check():
    """Eksekusi 1 siklus pemantauan tiket pesawat."""
    print("=" * 60)
    print(f"⏰ [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Memulai Siklus Pengecekan Tiket Pesawat")
    print(f"📍 Rute: {ORIGIN} -> {DESTINATION}")
    print(f"📅 Tanggal: {', '.join(TARGET_DATES)}")
    print(f"💵 Target Harga: Rp {MIN_AFFORDABLE_PRICE:,.0f} - Rp {MAX_AFFORDABLE_PRICE:,.0f}")
    print("=" * 60)

    db = TicketDatabase()
    notifier = TelegramNotifier()
    scraper = FlightScraper()

    # 1. Scraping data penerbangan
    all_flights = scraper.search_all_target_dates()
    print(f"📊 Total penerbangan ditemukan: {len(all_flights)} penerbangan.")

    # 2. Filter penerbangan dalam range harga terjangkau (<= MAX_AFFORDABLE_PRICE)
    affordable_flights = [
        f for f in all_flights if f["price"] <= MAX_AFFORDABLE_PRICE
    ]
    print(f"🎯 Penerbangan masuk kriteria harga (<= Rp {MAX_AFFORDABLE_PRICE:,.0f}): {len(affordable_flights)}")

    # Sort berdasarkan harga terendah
    affordable_flights.sort(key=lambda x: x["price"])

    new_alerts_sent = 0

    for flight in affordable_flights:
        formatted_price = f"Rp {flight['price']:,.0f}".replace(",", ".")
        print(f"   -> [{flight['departure_date']}] {flight['airline']} ({flight.get('flight_number')}): {formatted_price}")

        # 3. Cek database SQLite apakah perlu dinotifikasikan
        if db.should_notify(flight):
            print(f"🚨 Sinyal Baru! Mengirimkan notifikasi Telegram untuk {flight['airline']} ({formatted_price})...")
            
            sent = notifier.send_flight_alert(flight)
            if sent:
                db.record_notification(flight)
                new_alerts_sent += 1
            else:
                print("   ⚠️ Notifikasi gagal terkirim (pastikan TELEGRAM_BOT_TOKEN dan TELEGRAM_CHAT_ID sudah dikonfigurasi).")
        else:
            print("   ℹ️ Tiket ini sudah pernah dinotifikasikan sebelumnya dengan harga serupa. Skip anti-spam.")

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
        print(f"🚀 Menjalankan TicketAI dalam Mode Daemon (Setiap {CHECK_INTERVAL_MINUTES} menit)...")
        
        # Jalankan HTTP Health Check Server di background thread agar Render Web Service (FREE) gembira
        server_thread = threading.Thread(target=start_health_check_server, daemon=True)
        server_thread.start()

        # Jalankan siklus pertama secara langsung
        run_flight_check()

        # Setup scheduler berkala setiap X menit
        scheduler = BlockingScheduler()
        scheduler.add_job(run_flight_check, 'interval', minutes=CHECK_INTERVAL_MINUTES)
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
