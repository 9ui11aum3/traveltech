"""RouteIQ FastAPI backend — multimodal route search + user onboarding."""
import sqlite3
import os
from contextlib import asynccontextmanager
from typing import Optional

import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from routeiq.data import CITIES
from routeiq.router import find_routes, snap_to_nearest

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
    version="0.2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Geocoding ─────────────────────────────────────────────────────────────────

@app.get("/geocode")
async def geocode(q: str = Query(..., min_length=2)):
    """Autocomplete city search via Photon (open geocoder, no API key)."""
    CITY_TYPES = {"city", "town", "village", "municipality", "borough", "suburb", "district"}
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(
                "https://photon.komoot.io/api/",
                params={"q": q, "limit": 10, "lang": "en"},
            )
        features = resp.json().get("features", [])
    except Exception:
        features = []

    results = []
    seen = set()
    for f in features:
        p = f.get("properties", {})
        if p.get("osm_type") == "R" or p.get("type") in CITY_TYPES or p.get("osm_key") == "place":
            name = p.get("name", "")
            country = p.get("country", "")
            key = (name.lower(), country.lower())
            if key in seen or not name:
                continue
            seen.add(key)
            results.append({
                "name": name,
                "country": country,
                "state": p.get("state", ""),
                "lat": f["geometry"]["coordinates"][1],
                "lon": f["geometry"]["coordinates"][0],
            })
        if len(results) >= 6:
            break

    return results


# ── Route search ──────────────────────────────────────────────────────────────

@app.get("/routes")
def routes(
    from_city: Optional[str] = Query(None, alias="from", description="Origin city slug (legacy)"),
    to: Optional[str] = Query(None, description="Destination city slug (legacy)"),
    from_lat: Optional[float] = Query(None),
    from_lon: Optional[float] = Query(None),
    to_lat: Optional[float] = Query(None),
    to_lon: Optional[float] = Query(None),
    from_name: Optional[str] = Query(None, description="Display name for origin"),
    to_name: Optional[str] = Query(None, description="Display name for destination"),
):
    """Return fastest / cheapest / greenest routes between two cities.

    Accepts either city slugs (legacy) or lat/lon coordinates.
    When coordinates are provided, snaps to the nearest node in the route graph.
    """
    # Resolve origin
    if from_lat is not None and from_lon is not None:
        origin_slug, origin_snap_km = snap_to_nearest(from_lat, from_lon)
        origin_display = from_name or origin_slug
    elif from_city:
        origin_slug = from_city.lower()
        origin_snap_km = 0.0
        origin_display = from_name or (CITIES.get(origin_slug, {}).get("name", origin_slug))
    else:
        raise HTTPException(status_code=400, detail="Provide 'from' slug or 'from_lat'+'from_lon'")

    # Resolve destination
    if to_lat is not None and to_lon is not None:
        dest_slug, dest_snap_km = snap_to_nearest(to_lat, to_lon)
        dest_display = to_name or dest_slug
    elif to:
        dest_slug = to.lower()
        dest_snap_km = 0.0
        dest_display = to_name or (CITIES.get(dest_slug, {}).get("name", dest_slug))
    else:
        raise HTTPException(status_code=400, detail="Provide 'to' slug or 'to_lat'+'to_lon'")

    result = find_routes(
        origin_slug,
        dest_slug,
        origin_display=origin_display,
        destination_display=dest_display,
        origin_snap_km=origin_snap_km,
        destination_snap_km=dest_snap_km,
    )
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@app.get("/snap")
def snap(lat: float = Query(...), lon: float = Query(...)):
    """Return the nearest hub city slug for given coordinates."""
    slug, dist_km = snap_to_nearest(lat, lon)
    city = CITIES[slug]
    return {"slug": slug, "name": city["name"], "country": city["country"], "distance_km": round(dist_km)}


@app.get("/cities")
def cities():
    """Return the list of supported hub cities."""
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
    return {"status": "ok", "version": "0.2.0"}
