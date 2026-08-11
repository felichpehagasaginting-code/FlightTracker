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
        """Inisialisasi tabel SQLite untuk histori notifikasi tiket."""
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
            conn.commit()

    @staticmethod
    def generate_flight_key(airline: str, departure_date: str, departure_time: str, arrival_time: str) -> str:
        """Menghasilkan unique key untuk identifikasi rute penerbangan spesifik."""
        raw_key = f"{airline.lower().strip()}_{departure_date}_{departure_time.strip()}_{arrival_time.strip()}"
        return hashlib.md5(raw_key.encode("utf-8")).hexdigest()

    def should_notify(self, flight_info: Dict[str, Any]) -> bool:
        """
        Mengecek apakah tiket perlu dinotifikasi:
        - True jika tiket belum pernah dinotifikasi.
        - True jika harga tiket baru lebih murah dibanding yang pernah dinotifikasi sebelumnya.
        - False jika tiket sudah pernah dinotifikasi dengan harga yang sama atau lebih murah.
        """
        flight_key = flight_info.get("flight_key") or self.generate_flight_key(
            flight_info["airline"],
            flight_info["departure_date"],
            flight_info.get("departure_time", ""),
            flight_info.get("arrival_time", "")
        )
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
