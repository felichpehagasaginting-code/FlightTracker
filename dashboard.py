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

@app.get("/", response_class=HTMLResponse)
def dashboard_ui():
    html_file = TEMPLATES_DIR / "index.html"
    if html_file.exists():
        return HTMLResponse(content=html_file.read_text(encoding="utf-8"), status_code=200)
    return HTMLResponse(content="<h1>Dashboard UI HTML not found</h1>", status_code=404)
