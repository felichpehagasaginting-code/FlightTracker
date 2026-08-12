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
        self.sticker_id = os.getenv("TELEGRAM_STICKER_ID", "")
        self.api_url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        self.sticker_api_url = f"https://api.telegram.org/bot{self.token}/sendSticker"


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


    def send_message(self, text: str, parse_mode: str = "HTML") -> bool:
        """Mengirim pesan langsung ke Telegram via REST API."""
        if not self.is_configured():
            print("⚠️ Telegram Notifier belum dikonfigurasi (TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID kosong).")
            return False

        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": False
        }

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

    def send_sticker(self, sticker_id: str = None) -> bool:
        """Mengirim stiker ke Telegram via sendSticker API endpoint (WebP/TGS/WebM atau Sticker File ID)."""
        target_sticker = sticker_id or self.sticker_id
        if not target_sticker:
            return False
        if not self.is_configured():
            print("⚠️ Telegram Notifier belum dikonfigurasi.")
            return False

        payload = {
            "chat_id": self.chat_id,
            "sticker": target_sticker
        }
        try:
            response = requests.post(self.sticker_api_url, json=payload, timeout=10)
            result = response.json()
            if response.status_code == 200 and result.get("ok"):
                print("🎨 Stiker Telegram berhasil terkirim!")
                return True
            else:
                print(f"⚠️ Gagal mengirim stiker: {result.get('description')}")
                return False
        except Exception as e:
            print(f"❌ Error HTTP Telegram Sticker API: {e}")
            return False

    def send_flight_alert(self, flight_info: Dict[str, Any]) -> bool:
        """Mengirim pesan sinyal tiket pesawat murah dalam format siap pakai."""
        price = int(flight_info["price"])
        formatted_price = f"Rp {price:,.0f}".replace(",", ".")

        # Klasifikasi Kategori Deal
        if price < 1300000:
            deal_badge = "🚨 SUPER CHEAP DEAL"
        elif price <= 1450000:
            deal_badge = "🟢 DEAL BAGUS BANGET"
        else:
            deal_badge = "🟡 TARGET AFFORDABLE"

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
            f"⏱️ <b>Durasi:</b> {flight_info.get('duration', '2j 15m')}\n\n"
            f"🔗 <a href='{booking_link}'>Klik Di Sini Untuk Pesan Tiket</a>\n"
            f"-------------------------------------------\n"
            f"🤖 <i>TicketAI Automated Tracker</i>"
        )

        # Jika TELEGRAM_STICKER_ID diset, kirim stiker terlebih dahulu
        if self.sticker_id:
            self.send_sticker()

        return self.send_message(message, parse_mode="HTML")

    def send_test_notification(self) -> bool:
        test_info = {
            "airline": "Batik Air",
            "flight_number": "ID-6881",
            "departure_date": "Jumat, 18 September 2026",
            "departure_time": "08:30 WIB",
            "arrival_time": "10:50 WIB",
            "duration": "2j 20m",
            "price": 1420000,
            "booking_link": "https://www.google.com/travel/flights"
        }
        return self.send_flight_alert(test_info)
