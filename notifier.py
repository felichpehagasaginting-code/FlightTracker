import os
import requests
from typing import Dict, Any

class TelegramNotifier:
    def __init__(self, token: str = None, chat_id: str = None):
        from dotenv import load_dotenv
        from config import BASE_DIR
        load_dotenv(BASE_DIR / ".env", override=True)

        self.token = token or os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID", "")
        self.api_url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        self.doc_api_url = f"https://api.telegram.org/bot{self.token}/sendDocument"


    def is_configured(self) -> bool:
        if not self.token:
            return False
        if not self.chat_id:
            # Coba auto-discover chat_id dari getUpdates
            discovered_id = self.auto_discover_chat_id()
            if discovered_id:
                self.chat_id = discovered_id
                return True
            return False
        return True

    def auto_discover_chat_id(self) -> str:
        """Mengambil chat_id secara otomatis dari pesan terakhir yang masuk ke bot."""
        if not self.token:
            return ""
        try:
            url = f"https://api.telegram.org/bot{self.token}/getUpdates"
            res = requests.get(url, timeout=10).json()
            if res.get("ok") and res.get("result"):
                # Ambil chat_id dari pesan terakhir
                last_update = res["result"][-1]
                chat_id = str(last_update.get("message", {}).get("chat", {}).get("id") or 
                             last_update.get("channel_post", {}).get("chat", {}).get("id") or "")
                if chat_id:
                    print(f"✨ Chat ID Telegram berhasil dideteksi otomatis: {chat_id}")
                    # Simpan ke .env
                    self._save_chat_id_to_env(chat_id)
                    return chat_id
        except Exception as e:
            print(f"ℹ️ Auto-discover chat ID error: {e}")
        return ""

    def _save_chat_id_to_env(self, chat_id: str):
        try:
            from config import BASE_DIR
            env_path = BASE_DIR / ".env"
            if env_path.exists():
                content = env_path.read_text(encoding="utf-8")
                if "TELEGRAM_CHAT_ID=" in content:
                    lines = content.splitlines()
                    new_lines = []
                    for line in lines:
                        if line.startswith("TELEGRAM_CHAT_ID="):
                            new_lines.append(f"TELEGRAM_CHAT_ID={chat_id}")
                        else:
                            new_lines.append(line)
                    env_path.write_text("\n".join(new_lines), encoding="utf-8")
        except Exception as e:
            print(f"⚠️ Gagal menyimpan CHAT_ID ke .env: {e}")


    def send_message(self, text: str, parse_mode: str = "HTML", reply_markup: dict = None) -> bool:
        """Mengirim pesan langsung ke Telegram via REST API (dengan opsional Inline Keyboard)."""
        if not self.is_configured():
            print("⚠️ Telegram Notifier belum dikonfigurasi (TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID kosong).")
            return False

        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": False
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup

        try:
            response = requests.post(self.api_url, json=payload, timeout=10)
            result = response.json()
            if response.status_code == 200 and result.get("ok"):
                print("✅ Sinyal Telegram berhasil terkirim!")
                return True
            else:
                print(f"❌ Gagal mengirim pesan Telegram: {result.get('description')}")
                return False
        except Exception as e:
            print(f"❌ Error HTTP Telegram API: {e}")
            return False

    def send_svg_sticker(self, sticker_name: str) -> bool:
        """Mengirim file stiker SVG lokal (vektor graphic) ke Telegram via sendDocument API endpoint."""
        from config import ENABLE_SVG_STICKERS, STICKERS_DIR
        if not ENABLE_SVG_STICKERS:
            return False
        if not self.is_configured():
            print("⚠️ Telegram Notifier belum dikonfigurasi.")
            return False

        svg_path = STICKERS_DIR / sticker_name
        if not svg_path.exists():
            print(f"⚠️ File stiker SVG tidak ditemukan: {svg_path}")
            return False

        try:
            with open(svg_path, "rb") as f:
                files = {"document": (svg_path.name, f, "image/svg+xml")}
                data = {"chat_id": self.chat_id}
                response = requests.post(self.doc_api_url, data=data, files=files, timeout=15)
                result = response.json()
                if response.status_code == 200 and result.get("ok"):
                    print(f"🎨 Stiker SVG ({svg_path.name}) berhasil terkirim!")
                    return True
                else:
                    print(f"⚠️ Gagal mengirim stiker SVG: {result.get('description')}")
                    return False
        except Exception as e:
            print(f"❌ Error HTTP Telegram Document API for SVG: {e}")
            return False

    def send_flight_alert(self, flight_info: Dict[str, Any]) -> bool:
        """Mengirim pesan sinyal tiket pesawat murah dalam format siap pakai dengan Inline Keyboard."""
        from database import TicketDatabase
        price = int(flight_info["price"])
        formatted_price = f"Rp {price:,.0f}".replace(",", ".")

        flight_key = flight_info.get("flight_key") or TicketDatabase.generate_flight_key(
            flight_info["airline"],
            flight_info["departure_date"],
            flight_info.get("departure_time", ""),
            flight_info.get("arrival_time", "")
        )

        # Klasifikasi Kategori Deal & Stiker SVG (Dynamic Config)
        import config
        min_p = config.MIN_AFFORDABLE_PRICE
        max_p = config.MAX_AFFORDABLE_PRICE

        if price < min_p:
            deal_badge = "🚨 SUPER CHEAP DEAL"
            sticker_file = "super_cheap.svg"
        elif price <= 1450000:
            deal_badge = "🟢 DEAL BAGUS BANGET"
            sticker_file = "good_deal.svg"
        else:
            deal_badge = f"🟡 TARGET AFFORDABLE (<= {f'Rp {max_p:,.0f}'.replace(',', '.')})"
            sticker_file = "affordable.svg"

        # Kirim Stiker SVG lokal sesuai kategori deal
        self.send_svg_sticker(sticker_file)

        booking_link = flight_info.get("booking_link", "https://www.google.com/travel/flights")
        flight_num = flight_info.get("flight_number")
        flight_str = f" ({flight_num})" if flight_num else ""

        message = (
            f"✈️ <b>SINYAL TIKET PESAWAT MURAH!</b>\n"
            f"<b>Status:</b> {deal_badge}\n"
            f"<b>Tipe:</b> Sekali Jalan (One-Way)\n\n"
            f"📍 <b>Rute:</b> Medan (KNO) ➡️ Jakarta (CGK)\n"
            f"📅 <b>Tanggal:</b> {flight_info['departure_date']}\n"
            f"💵 <b>Harga:</b> <b>{formatted_price}</b>\n\n"
            f"🏢 <b>Maskapai:</b> {flight_info['airline']}{flight_str}\n"
            f"🕒 <b>Waktu:</b> {flight_info.get('departure_time', '-')} - {flight_info.get('arrival_time', '-')} (Direct)\n"
            f"⏱️ <b>Durasi:</b> {flight_info.get('duration') or 'Tidak Diketahui'}\n\n"
            f"-------------------------------------------\n"
            f"🤖 <i>TicketAI Automated Tracker</i>"
        )

        # Telegram Inline Keyboard Buttons
        reply_markup = {
            "inline_keyboard": [
                [
                    {"text": "🎫 Pesan Tiket Sekarang", "url": booking_link}
                ],
                [
                    {"text": "🔕 Mute Penerbangan Ini", "callback_data": f"mute_{flight_key}"}
                ]
            ]
        }

        return self.send_message(message, parse_mode="HTML", reply_markup=reply_markup)

    def send_daily_digest(self) -> bool:
        """Mengirimkan laporan ringkasan harian (Daily Digest) jam 08:00 pagi."""
        from database import TicketDatabase
        db = TicketDatabase()
        summary = db.get_daily_summary()

        cheapest_list = summary.get("cheapest", [])
        avg_price = summary.get("avg_price", 0)

        if not cheapest_list:
            return False

        lines = [
            "📊 <b>TICKETAI DAILY DIGEST REPORT</b>",
            "-------------------------------------------",
            f"💵 <b>Harga Rata-Rata 24j:</b> Rp {avg_price:,.0f}".replace(",", "."),
            "\n🏆 <b>5 Tiket Termurah Hari Ini:</b>"
        ]

        for i, item in enumerate(cheapest_list, 1):
            p = int(item["price"])
            p_str = f"Rp {p:,.0f}".replace(",", ".")
            lines.append(f"{i}. <b>{item['airline']}</b> ({item['departure_date']}): {p_str}")

        lines.append("\n-------------------------------------------")
        lines.append("🤖 <i>TicketAI Automated Daily Summary</i>")

        return self.send_message("\n".join(lines), parse_mode="HTML")

    def register_bot_commands(self):
        """Mendaftarkan daftar perintah bot ke API Telegram agar muncul di tombol Menu Telegram."""
        if not self.token:
            return
        try:
            url = f"https://api.telegram.org/bot{self.token}/setMyCommands"
            commands = [
                {"command": "scan", "description": "Picu pengecekan & pengikisan tiket instan"},
                {"command": "status", "description": "Lihat statistik & status kesehatan tracker 24/7"},
                {"command": "dates", "description": "Lihat daftar tanggal target keberangkatan"},
                {"command": "digest", "description": "Kirim ringkasan harian 5 tiket termurah"},
                {"command": "help", "description": "Tampilkan daftar panduan perintah bot"}
            ]
            requests.post(url, json={"commands": commands}, timeout=10)
            print("✨ Command menu Telegram bot berhasil terdaftar!")
        except Exception as e:
            print(f"⚠️ Gagal mendaftarkan bot commands ke Telegram: {e}")

    def listen_bot_updates(self):
        """Looping listener 2-arah untuk mendengarkan perintah & tombol dari chat Telegram."""
        import time
        from database import TicketDatabase
        db = TicketDatabase()
        last_update_id = 0

        self.register_bot_commands()
        print("🤖 Telegram Bot Listener 2-Arah aktif...")

        while True:
            try:
                url = f"https://api.telegram.org/bot{self.token}/getUpdates?offset={last_update_id + 1}&timeout=10"
                res = requests.get(url, timeout=15).json()

                if res.get("ok") and res.get("result"):
                    for update in res["result"]:
                        last_update_id = update["update_id"]

                        # Handle Callback Query (Tombol Inline)
                        if "callback_query" in update:
                            cb = update["callback_query"]
                            cb_data = cb.get("data", "")
                            cb_id = cb.get("id")

                            if cb_data.startswith("mute_"):
                                f_key = cb_data.replace("mute_", "")
                                db.mute_flight(f_key)
                                # Answer callback
                                requests.post(f"https://api.telegram.org/bot{self.token}/answerCallbackQuery", json={
                                    "callback_query_id": cb_id,
                                    "text": "✅ Penerbangan ini telah di-mute!"
                                })

                        # Handle Messages (Command /scan, /check, /status, /help, dll)
                        elif "message" in update:
                            msg = update["message"]
                            text = msg.get("text", "").strip()
                            cmd = text.split("@")[0].lower()

                            if cmd in ["/scan", "/check", "/run"]:
                                self.send_message("🔄 <b>Menjalankan pemantauan & pengikisan tiket secara instan...</b>")
                                from main import run_flight_check
                                run_flight_check()

                            elif cmd in ["/status", "/mode", "/stats"]:
                                stats = db.get_dashboard_stats()
                                import config
                                status_msg = (
                                    "📊 <b>STATUS TICKETAI TRACKER (24/7 LIVE)</b>\n"
                                    "-------------------------------------------\n"
                                    f"✅ <b>Total Scans Executed:</b> {stats['total_scans']}\n"
                                    f"🚨 <b>Total Signals Sent:</b> {stats['total_alerts']}\n"
                                    f"💵 <b>Lowest Price Recorded:</b> Rp {stats['lowest_price']:,.0f}\n"
                                    f"📅 <b>Target Dates:</b> {', '.join(config.TARGET_DATES)}\n"
                                    f"🎯 <b>Active Price Cap:</b> Rp {config.MAX_AFFORDABLE_PRICE:,.0f}\n"
                                    f"⏱️ <b>Scan Interval:</b> {config.CHECK_INTERVAL_MINUTES} menit\n"
                                    "-------------------------------------------\n"
                                    "🤖 <i>TicketAI Bot Listener Active</i>"
                                ).replace(",", ".")
                                self.send_message(status_msg)

                            elif cmd in ["/dates", "/tanggal"]:
                                import config
                                self.send_message(f"📅 <b>Tanggal Target Aktif:</b>\n" + "\n".join([f"• {d}" for d in config.TARGET_DATES]))

                            elif cmd in ["/digest", "/summary"]:
                                self.send_daily_digest()

                            elif cmd.startswith("/") or cmd in ["help", "menu", "bantuan"]:
                                help_msg = (
                                    "🤖 <b>TICKETAI TELEGRAM BOT COMMANDS</b>\n"
                                    "-------------------------------------------\n"
                                    "<b>Daftar Perintah & Kegunaannya:</b>\n\n"
                                    "✈️ <b>/scan</b> atau <b>/check</b>\n"
                                    "<i>Memicu pemantauan & pengikisan tiket live secara instan di background.</i>\n\n"
                                    "📊 <b>/status</b> atau <b>/mode</b>\n"
                                    "<i>Melihat status kesehatan bot 24/7, total scan, harga terendah, & target price cap aktif.</i>\n\n"
                                    "📅 <b>/dates</b>\n"
                                    "<i>Menampilkan daftar tanggal keberangkatan target yang sedang dipantau.</i>\n\n"
                                    "🏆 <b>/digest</b>\n"
                                    "<i>Mengirimkan ringkasan harian 5 tiket pesawat termurah yang pernah terdeteksi.</i>\n\n"
                                    "❓ <b>/help</b>\n"
                                    "<i>Menampilkan menu panduan perintah bot ini.</i>\n"
                                    "-------------------------------------------\n"
                                    "🤖 <i>TicketAI Automated Assistant</i>"
                                )
                                self.send_message(help_msg)

            except Exception as e:
                time.sleep(5)

            time.sleep(3)

    def send_test_notification(self) -> bool:
        """Mengirim notifikasi uji coba FORMAT pesan (BUKAN data penerbangan real)."""
        test_info = {
            "airline": "[TEST] Batik Air",
            "flight_number": "ID-XXXX",
            "departure_date": "18 September 2026",
            "departure_time": "08:30",
            "arrival_time": "10:50",
            "duration": "2j 20m",
            "price": 1420000,
            "booking_link": "https://www.google.com/travel/flights"
        }
        print("⚠️  PERINGATAN: Data ini adalah data UJI COBA FORMAT, bukan data penerbangan real.")
        return self.send_flight_alert(test_info)
