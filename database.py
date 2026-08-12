import sqlite3
import hashlib
from typing import Dict, Any, Optional
from config import DATABASE_PATH

class TicketDatabase:
    def __init__(self, db_path=DATABASE_PATH):
        self.db_path = str(db_path)
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        """Inisialisasi tabel SQLite untuk histori notifikasi, riwayat harga, dan muted flights."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notified_tickets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    flight_key TEXT UNIQUE NOT NULL,
                    airline TEXT NOT NULL,
                    flight_number TEXT,
                    departure_date TEXT NOT NULL,
                    departure_time TEXT,
                    arrival_time TEXT,
                    price INTEGER NOT NULL,
                    booking_link TEXT,
                    notified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS price_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    flight_key TEXT NOT NULL,
                    airline TEXT NOT NULL,
                    departure_date TEXT NOT NULL,
                    departure_time TEXT,
                    arrival_time TEXT,
                    price INTEGER NOT NULL,
                    scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS muted_flights (
                    flight_key TEXT PRIMARY KEY,
                    muted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    @staticmethod
    def generate_flight_key(airline: str, departure_date: str, departure_time: str, arrival_time: str) -> str:
        """Menghasilkan unique key untuk identifikasi rute penerbangan spesifik."""
        raw_key = f"{airline.lower().strip()}_{departure_date}_{departure_time.strip()}_{arrival_time.strip()}"
        return hashlib.md5(raw_key.encode("utf-8")).hexdigest()

    def is_flight_muted(self, flight_key: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM muted_flights WHERE flight_key = ?", (flight_key,))
            return cursor.fetchone() is not None

    def mute_flight(self, flight_key: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO muted_flights (flight_key) VALUES (?)", (flight_key,))
            conn.commit()
            return True

    def record_price_snapshots(self, flights: list):
        """Mencatat seluruh data hasil scan penerbangan ke histori harga."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            for flight_info in flights:
                flight_key = flight_info.get("flight_key") or self.generate_flight_key(
                    flight_info["airline"],
                    flight_info["departure_date"],
                    flight_info.get("departure_time", ""),
                    flight_info.get("arrival_time", "")
                )
                cursor.execute("""
                    INSERT INTO price_history (
                        flight_key, airline, departure_date, departure_time, arrival_time, price
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    flight_key,
                    flight_info.get("airline", "Unknown"),
                    flight_info["departure_date"],
                    flight_info.get("departure_time", "-"),
                    flight_info.get("arrival_time", "-"),
                    int(flight_info["price"])
                ))
            conn.commit()

    def should_notify(self, flight_info: Dict[str, Any]) -> bool:
        """
        Mengecek apakah tiket perlu dinotifikasi:
        - True jika tiket belum pernah dinotifikasi dan tidak di-mute.
        - True jika harga tiket baru lebih murah dibanding yang pernah dinotifikasi sebelumnya.
        - False jika tiket di-mute atau harga tidak berubah.
        """
        flight_key = flight_info.get("flight_key") or self.generate_flight_key(
            flight_info["airline"],
            flight_info["departure_date"],
            flight_info.get("departure_time", ""),
            flight_info.get("arrival_time", "")
        )
        if self.is_flight_muted(flight_key):
            return False

        price = int(flight_info["price"])

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT price FROM notified_tickets WHERE flight_key = ?", (flight_key,))
            row = cursor.fetchone()

            if row is None:
                return True
            
            existing_price = row[0]
            if price < existing_price:
                return True
            
            return False

    def record_notification(self, flight_info: Dict[str, Any]):
        """Menyimpan atau memperbarui data penerbangan yang sudah dinotifikasikan."""
        flight_key = flight_info.get("flight_key") or self.generate_flight_key(
            flight_info["airline"],
            flight_info["departure_date"],
            flight_info.get("departure_time", ""),
            flight_info.get("arrival_time", "")
        )
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO notified_tickets (
                    flight_key, airline, flight_number, departure_date, 
                    departure_time, arrival_time, price, booking_link
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(flight_key) DO UPDATE SET
                    price = excluded.price,
                    notified_at = CURRENT_TIMESTAMP
            """, (
                flight_key,
                flight_info.get("airline", "Unknown"),
                flight_info.get("flight_number", "-"),
                flight_info["departure_date"],
                flight_info.get("departure_time", "-"),
                flight_info.get("arrival_time", "-"),
                int(flight_info["price"]),
                flight_info.get("booking_link", "")
            ))
            conn.commit()

    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Mengambil data agregat statistik untuk UI Dashboard."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM price_history")
            total_scans = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM notified_tickets")
            total_alerts = cursor.fetchone()[0]

            cursor.execute("SELECT MIN(price) FROM price_history")
            lowest_price = cursor.fetchone()[0] or 0

            cursor.execute("SELECT COUNT(DISTINCT flight_key) FROM price_history")
            unique_flights = cursor.fetchone()[0]

            return {
                "total_scans": total_scans,
                "total_alerts": total_alerts,
                "lowest_price": lowest_price,
                "unique_flights": unique_flights
            }

    def get_all_recent_flights(self, limit: int = 50) -> list:
        """Mengambil daftar penerbangan hasil scan terbaru."""
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT flight_key, airline, departure_date, departure_time, arrival_time, price, scanned_at
                FROM price_history
                ORDER BY scanned_at DESC
                LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_price_trends(self) -> list:
        """Mengambil data tren harga rata-rata per tanggal untuk Chart.js."""
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT departure_date, airline, MIN(price) as min_price, AVG(price) as avg_price
                FROM price_history
                GROUP BY departure_date, airline
                ORDER BY departure_date ASC
            """)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_daily_summary(self) -> Dict[str, Any]:
        """Mengambil data ringkasan harian untuk Telegram Daily Digest."""
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT airline, departure_date, departure_time, arrival_time, price
                FROM price_history
                WHERE scanned_at >= datetime('now', '-1 day')
                ORDER BY price ASC
                LIMIT 5
            """)
            cheapest_today = [dict(row) for row in cursor.fetchall()]

            cursor.execute("SELECT AVG(price) as avg_p FROM price_history WHERE scanned_at >= datetime('now', '-1 day')")
            row = cursor.fetchone()
            avg_price = int(row["avg_p"]) if row and row["avg_p"] else 0

            return {
                "cheapest": cheapest_today,
                "avg_price": avg_price
            }
