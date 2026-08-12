import os
import sys
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from database import TicketDatabase
from config import BASE_DIR, ORIGIN, DESTINATION, TARGET_DATES, MIN_AFFORDABLE_PRICE, MAX_AFFORDABLE_PRICE, CHECK_INTERVAL_MINUTES

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="TicketAI Operations Dashboard", docs_url=None, redoc_url=None)

# Allow Cross-Origin Requests (CORS) for Live Server & Web Dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TEMPLATES_DIR = BASE_DIR / "templates"
TEMPLATES_DIR.mkdir(exist_ok=True)
db = TicketDatabase()

FRONTEND_DIST_DIR = BASE_DIR / "frontend" / "dist"

if (FRONTEND_DIST_DIR / "assets").exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST_DIR / "assets")), name="static_assets")

@app.get("/health", response_class=HTMLResponse)
def health_check():
    return HTMLResponse("✅ FlightTracker Bot is running 24/7!", status_code=200)

@app.get("/api/stats")
def get_stats():
    stats = db.get_dashboard_stats()
    return JSONResponse({
        "status": "online",
        "route": f"{ORIGIN} -> {DESTINATION}",
        "target_dates": TARGET_DATES,
        "price_cap": MAX_AFFORDABLE_PRICE,
        "check_interval_min": CHECK_INTERVAL_MINUTES,
        "stats": stats
    })

@app.get("/api/flights")
def get_flights(limit: int = 50):
    flights = db.get_all_recent_flights(limit=limit)
    return JSONResponse(flights)

@app.get("/api/trends")
def get_trends():
    trends = db.get_price_trends()
    return JSONResponse(trends)

@app.post("/api/trigger-check")
def trigger_check(background_tasks: BackgroundTasks):
    try:
        from main import run_flight_check
        background_tasks.add_task(run_flight_check)
        return JSONResponse({"status": "success", "message": "Proses pengecekan tiket manual berhasil dipicu di background!"})
    except Exception as e:
        return JSONResponse({"status": "error", "message": f"Gagal memicu scan: {str(e)}"}, status_code=500)

@app.get("/api/settings")
def get_settings():
    import config
    return JSONResponse({
        "max_price_cap": config.MAX_AFFORDABLE_PRICE,
        "min_price_target": config.MIN_AFFORDABLE_PRICE,
        "check_interval_min": config.CHECK_INTERVAL_MINUTES,
        "origin": config.ORIGIN,
        "destination": config.DESTINATION,
        "target_dates": config.TARGET_DATES,
        "telegram_configured": bool(config.TELEGRAM_BOT_TOKEN and config.TELEGRAM_CHAT_ID)
    })

@app.post("/api/settings")
def update_settings(payload: dict, background_tasks: BackgroundTasks):
    import config
    try:
        if "max_price_cap" in payload:
            config.MAX_AFFORDABLE_PRICE = int(payload["max_price_cap"])
        if "min_price_target" in payload:
            config.MIN_AFFORDABLE_PRICE = int(payload["min_price_target"])
        if "check_interval_min" in payload:
            config.CHECK_INTERVAL_MINUTES = int(payload["check_interval_min"])

        # Evaluasi adaptif sinyal Telegram secara langsung
        from main import evaluate_and_send_alerts
        alerts_sent = evaluate_and_send_alerts()

        msg = "Pengaturan threshold & interval berhasil diperbarui!"
        if alerts_sent > 0:
            msg += f" 🚨 {alerts_sent} Sinyal Telegram baru otomatis terkirim!"

        return JSONResponse({
            "status": "success",
            "message": msg,
            "alerts_sent": alerts_sent,
            "settings": {
                "max_price_cap": config.MAX_AFFORDABLE_PRICE,
                "min_price_target": config.MIN_AFFORDABLE_PRICE,
                "check_interval_min": config.CHECK_INTERVAL_MINUTES
            }
        })
    except Exception as e:
        return JSONResponse({"status": "error", "message": f"Gagal memperbarui pengaturan: {str(e)}"}, status_code=400)

@app.get("/api/telegram/logs")
def get_telegram_logs(limit: int = 20):
    logs = db.get_notification_logs(limit=limit)
    return JSONResponse(logs)

@app.post("/api/telegram/test")
def send_telegram_test():
    try:
        from notifier import TelegramNotifier
        notifier = TelegramNotifier()
        sample_flight = {
            "origin": ORIGIN,
            "destination": DESTINATION,
            "airline": "Garuda Indonesia (TEST SIGNAL)",
            "flight_number": "GA-188",
            "departure_date": TARGET_DATES[0] if TARGET_DATES else "2026-09-18",
            "departure_time": "08:30 WIB",
            "arrival_time": "10:50 WIB",
            "duration": "2j 20m",
            "price": 1420000,
            "booking_link": "https://www.google.com/travel/flights"
        }
        sent = notifier.send_flight_alert(sample_flight)
        if sent:
            db.record_notification(sample_flight)
            return JSONResponse({
                "status": "success",
                "message": "🟢 Sinyal uji coba Telegram berhasil dikirim ke chat Anda!"
            })
        else:
            return JSONResponse({
                "status": "error",
                "message": "⚠️ Gagal mengirim sinyal Telegram. Pastikan BOT_TOKEN dan CHAT_ID sudah benar."
            }, status_code=400)
    except Exception as e:
        return JSONResponse({"status": "error", "message": f"Error pengujian bot: {str(e)}"}, status_code=500)


@app.get("/", response_class=HTMLResponse)
def dashboard_ui():
    dist_index = FRONTEND_DIST_DIR / "index.html"
    if dist_index.exists():
        return HTMLResponse(content=dist_index.read_text(encoding="utf-8"), status_code=200)
    
    html_file = TEMPLATES_DIR / "index.html"
    if html_file.exists():
        return HTMLResponse(content=html_file.read_text(encoding="utf-8"), status_code=200)
    return HTMLResponse(content="<h1>Dashboard UI HTML not found</h1>", status_code=404)

