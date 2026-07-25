"""RouteIQ FastAPI backend — multimodal route search + user onboarding."""
import sqlite3
import os
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from routeiq.data import CITIES
from routeiq.router import find_routes

DB_PATH = os.getenv("DB_PATH", "/data/routeiq.db")


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            home_city TEXT NOT NULL,
            travel_style TEXT NOT NULL DEFAULT 'balanced',
            carbon_sensitivity TEXT NOT NULL DEFAULT 'medium',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="RouteIQ API",
    description="Multimodal European route search — open data, no paid APIs.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Route search ──────────────────────────────────────────────────────────────

@app.get("/routes")
def routes(
    from_city: str = Query(..., alias="from", description="Origin city slug"),
    to: str = Query(..., description="Destination city slug"),
):
    """Return fastest / cheapest / greenest routes between two cities."""
    result = find_routes(from_city.lower(), to.lower())
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@app.get("/cities")
def cities():
    """Return the list of supported cities."""
    return [
        {"id": k, "name": v["name"], "country": v["country"], "lat": v["lat"], "lon": v["lon"]}
        for k, v in sorted(CITIES.items(), key=lambda x: x[1]["name"])
    ]


# ── Onboarding / user preferences ────────────────────────────────────────────

class UserPreferences(BaseModel):
    email: str
    home_city: str
    travel_style: str = "balanced"   # fast | cheap | green | balanced
    carbon_sensitivity: str = "medium"  # low | medium | high


@app.post("/onboarding", status_code=201)
def onboarding(prefs: UserPreferences):
    """Save user travel preferences."""
    if prefs.home_city not in CITIES:
        raise HTTPException(status_code=400, detail="unknown_home_city")
    if prefs.travel_style not in {"fast", "cheap", "green", "balanced"}:
        raise HTTPException(status_code=400, detail="invalid_travel_style")
    if prefs.carbon_sensitivity not in {"low", "medium", "high"}:
        raise HTTPException(status_code=400, detail="invalid_carbon_sensitivity")

    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            "INSERT OR REPLACE INTO users (email, home_city, travel_style, carbon_sensitivity) VALUES (?,?,?,?)",
            (prefs.email, prefs.home_city, prefs.travel_style, prefs.carbon_sensitivity),
        )
        conn.commit()
    finally:
        conn.close()

    return {"status": "ok", "home_city": prefs.home_city}


@app.get("/onboarding/{email}")
def get_preferences(email: str):
    """Retrieve saved preferences for a user."""
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute(
        "SELECT email, home_city, travel_style, carbon_sensitivity FROM users WHERE email=?", (email,)
    ).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="user_not_found")
    return {
        "email": row[0],
        "home_city": row[1],
        "travel_style": row[2],
        "carbon_sensitivity": row[3],
    }


@app.get("/health")
def health():
    return {"status": "ok", "version": "0.1.0"}
