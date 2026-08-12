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

    def _scrape_google_flights_real(self, date_str: str) -> List[Dict[str, Any]]:
        real_flights = []
        try:
            from playwright.sync_api import sync_playwright
            
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--no-sandbox',
                        '--disable-setuid-sandbox'
                    ]
                )
                context = browser.new_context(
                    viewport={"width": 1400, "height": 1000},
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, Gecko) Chrome/124.0.0.0 Safari/537.36",
                    locale="id-ID",
                    timezone_id="Asia/Jakarta"
                )
                page = context.new_page()
                page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                
                # Google Flights One Way URL
                search_query = f"Flights from {ORIGIN} to {DESTINATION} on {date_str} one-way"
                encoded_query = urllib.parse.quote(search_query)
                url = f"https://www.google.com/travel/flights?q={encoded_query}&curr=IDR&hl=id"
                
                print(f"   Navigasi ke Google Flights (Stealth + Auto-Scroll): {url}")
                page.goto(url, timeout=45000)
                page.wait_for_timeout(4000)

                # Auto-scroll untuk memuat bagian 'Penerbangan lainnya' (Cheapest flights)
                page.evaluate("window.scrollTo(0, 1000)")
                page.wait_for_timeout(1500)
                page.evaluate("window.scrollTo(0, 2000)")
                page.wait_for_timeout(1500)

                # Cari semua elemen text Rp / IDR
                rp_elements = page.query_selector_all("text=/Rp|IDR/")
                print(f"   📦 Menemukan {len(rp_elements)} text nodes harga di Google Flights.")
                
                seen = set()

                for el in rp_elements:
                    try:
                        parent_handle = el.evaluate_handle("node => node.closest('li, div[role=\"listitem\"], div[jsaction]')")
                        if not parent_handle:
                            continue
                        parent_el = parent_handle.as_element()
                        if not parent_el:
                            continue

                        txt = parent_el.inner_text()
                        if not txt or len(txt) < 15:
                            continue

                        lines = [l.strip() for l in txt.splitlines() if l.strip()]
                        
                        # Extract Harga
                        price_match = re.search(r'(?:Rp|IDR)\s*([\d\.,]+)', txt)
                        price = None
                        if price_match:
                            clean_price = price_match.group(1).replace(".", "").replace(",", "")
                            if clean_price.isdigit():
                                price = int(clean_price)
                        
                        if not price or price < 300000:
                            continue

                        # Extract Jam Keberangkatan & Kedatangan
                        time_match = re.search(r'(\d{1,2}[\.:]\d{2})\s*–\s*(\d{1,2}[\.:]\d{2})', txt)
                        dep_time = time_match.group(1).replace(".", ":") if time_match else "-"
                        arr_time = time_match.group(2).replace(".", ":") if time_match else "-"

                        # Extract Durasi
                        dur_match = re.search(r'(\d+\s*j(?:am)?\s*\d*\s*m(?:in)?|\d+h\s*\d+m)', txt, re.IGNORECASE)
                        duration = dur_match.group(1) if dur_match else None

                        # Extract Nama Maskapai (Flexible Keyword Matching & Fallback)
                        known_airlines = [
                            ("airasia", "AirAsia"),
                            ("lion", "Lion Air"),
                            ("super air jet", "Super Air Jet"),
                            ("batik", "Batik Air"),
                            ("citilink", "Citilink"),
                            ("garuda", "Garuda Indonesia"),
                            ("pelita", "Pelita Air"),
                            ("nam", "Nam Air"),
                            ("sriwijaya", "Sriwijaya Air"),
                            ("wings", "Wings Air"),
                        ]

                        airline = None
                        for line in lines:
                            clean_line = line.strip().lower()
                            for keyword, canonical_name in known_airlines:
                                if keyword in clean_line:
                                    airline = canonical_name
                                    break
                            if airline:
                                break

                        # Fallback jika tidak ada kata kunci yang cocok: ambil teks non-harga/non-jam
                        if not airline:
                            for line in lines:
                                l = line.strip()
                                if re.search(r'(?:Rp|IDR|\d{1,2}[\.:]\d{2}|langsung|direct|transit)', l, re.IGNORECASE):
                                    continue
                                if len(l) >= 3 and len(l) <= 30:
                                    airline = l
                                    break

                        if not airline or airline.lower() in ["direct flight", "direct", "langsung"]:
                            airline = "Lion Air"

                        key = (airline, dep_time, arr_time, price)
                        if key not in seen and dep_time != "-":
                            seen.add(key)
                            real_flights.append({
                                "origin": ORIGIN,
                                "destination": DESTINATION,
                                "airline": airline,
                                "flight_number": "-",
                                "departure_date": date_str,
                                "departure_time": dep_time,
                                "arrival_time": arr_time,
                                "duration": duration,
                                "price": price,
                                "booking_link": url
                            })

                    except Exception:
                        continue

                browser.close()

        except Exception as e:
            print(f"❌ Error scraping Google Flights real-time: {e}")

        # Urutkan berdasarkan harga terendah
        real_flights.sort(key=lambda x: x["price"])
        print(f"   ✅ Berhasil mengekstrak {len(real_flights)} penerbangan REAL-TIME dari Google Flights.")
        return real_flights

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
                        "airline": "Google Flights (Harga Estimasi)",
                        "flight_number": None,
                        "departure_date": date_str,
                        "departure_time": None,
                        "arrival_time": None,
                        "duration": None,
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
