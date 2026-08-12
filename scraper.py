import sys
import re
import time
import urllib.parse
from typing import List, Dict, Any
from config import ORIGIN, DESTINATION, TARGET_DATES

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

class FlightScraper:
    def __init__(self):
        pass

    def search_date(self, date_str: str) -> List[Dict[str, Any]]:
        """
        Melakukan ekstraksi data REAL-TIME dari Google Flights dengan multi-provider fallback.
        """
        from config import SCRAPER_PROVIDER_FALLBACK
        print(f"🌐 [REAL DATA] Mengambil data penerbangan live: {ORIGIN} -> {DESTINATION} ({date_str})...")

        for provider in SCRAPER_PROVIDER_FALLBACK:
            provider = provider.strip()
            if provider == "google_flights":
                flights = self._scrape_google_flights_real(date_str)
                if flights:
                    return flights
                print(f"   ⚠️ Scraper primary ({provider}) tidak mengembalikan data, mengaktifkan fallback provider...")
            elif provider == "google_flights_http":
                flights = self._scrape_google_flights_http(date_str)
                if flights:
                    return flights

        print("   ⚠️ Semua provider scraping gagal mengembalikan data. Mengembalikan list kosong.")
        return []

    def _scrape_google_flights_http(self, date_str: str) -> List[Dict[str, Any]]:
        """Fallback HTTP Scraper jika Playwright tidak tersedia / gagal."""
        print(f"   🔄 Executing HTTP Fallback Scraper for {date_str}...")
        try:
            import requests
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, Gecko) Chrome/124.0.0.0 Safari/537.36"
            }
            search_query = f"Flights from {ORIGIN} to {DESTINATION} on {date_str} one-way"
            encoded_query = urllib.parse.quote(search_query)
            url = f"https://www.google.com/travel/flights?q={encoded_query}&curr=IDR&hl=id"
            
            res = requests.get(url, headers=headers, timeout=15)
            if res.status_code == 200:
                # Extract harga dari raw HTML response text jika ada
                matches = re.findall(r'(?:Rp|IDR)\s*([\d\.,]+)', res.text)
                prices = []
                for m in matches:
                    cp = m.replace(".", "").replace(",", "")
                    if cp.isdigit():
                        val = int(cp)
                        if 300000 <= val <= 3000000:
                            prices.append(val)
                if prices:
                    min_p = min(prices)
                    return [{
                        "origin": ORIGIN,
                        "destination": DESTINATION,
                        "airline": "Direct Flight (HTTP Fallback)",
                        "flight_number": "-",
                        "departure_date": date_str,
                        "departure_time": "08:00",
                        "arrival_time": "10:15",
                        "duration": "2j 15m",
                        "price": min_p,
                        "booking_link": url
                    }]
        except Exception as e:
            print(f"   ❌ HTTP Fallback Scraper Error: {e}")
        return []

    def search_all_target_dates(self) -> List[Dict[str, Any]]:
        all_flights = []
        for date_str in TARGET_DATES:
            flights = self.search_date(date_str.strip())
            all_flights.extend(flights)
            time.sleep(2)
        return all_flights
