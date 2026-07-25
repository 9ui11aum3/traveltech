"""Dijkstra-based multimodal route finder."""
import heapq
import math
from typing import Optional
from .data import GRAPH, CITIES


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))


def snap_to_nearest(lat: float, lon: float) -> tuple[str, float]:
    """Return (city_slug, distance_km) for the nearest graph node."""
    best_key, best_dist = "", float("inf")
    for key, city in CITIES.items():
        d = haversine_km(lat, lon, city["lat"], city["lon"])
        if d < best_dist:
            best_dist = d
            best_key = key
    return best_key, best_dist


def dijkstra(source: str, target: str, weight_key: str) -> Optional[dict]:
    dist = {source: 0.0}
    prev: dict = {}
    pq = [(0.0, source)]

    while pq:
        cost, u = heapq.heappop(pq)
        if cost > dist.get(u, float("inf")):
            continue
        if u == target:
            break
        for edge in GRAPH.get(u, []):
            nc = cost + edge[weight_key]
            if nc < dist.get(edge["to"], float("inf")):
                dist[edge["to"]] = nc
                prev[edge["to"]] = {"node": u, "edge": edge}
                heapq.heappush(pq, (nc, edge["to"]))

    if target not in dist:
        return None

    segments = []
    n = target
    while n in prev:
        entry = prev[n]
        segments.insert(0, {**entry["edge"], "from": entry["node"], "to": n})
        n = entry["node"]

    return {"total": dist[target], "segments": segments}


def find_routes(
    origin: str,
    destination: str,
    origin_display: Optional[str] = None,
    destination_display: Optional[str] = None,
    origin_snap_km: float = 0.0,
    destination_snap_km: float = 0.0,
) -> dict:
    if origin not in CITIES or destination not in CITIES:
        return {"error": "unknown_city"}
    if origin == destination and origin_snap_km < 1 and destination_snap_km < 1:
        return {"error": "same_city"}

    fast  = dijkstra(origin, destination, "duration")
    cheap = dijkstra(origin, destination, "price")
    green = dijkstra(origin, destination, "co2")

    def enrich(route: Optional[dict], label: str) -> Optional[dict]:
        if not route:
            return None
        segs = route["segments"]
        return {
            "label": label,
            "total_duration": sum(s["duration"] for s in segs),
            "total_price":    sum(s["price"]    for s in segs),
            "total_co2":      round(sum(s["co2"] for s in segs), 2),
            "transfers":      max(0, len(segs) - 1),
            "segments": [
                {
                    "from":      s["from"],
                    "from_name": CITIES[s["from"]]["name"],
                    "from_lat":  CITIES[s["from"]]["lat"],
                    "from_lon":  CITIES[s["from"]]["lon"],
                    "to":        s["to"],
                    "to_name":   CITIES[s["to"]]["name"],
                    "to_lat":    CITIES[s["to"]]["lat"],
                    "to_lon":    CITIES[s["to"]]["lon"],
                    "mode":      s["mode"],
                    "operator":  s["operator"],
                    "duration":  s["duration"],
                    "price":     s["price"],
                    "co2":       s["co2"],
                }
                for s in segs
            ],
        }

    last_mile_origin = (
        {
            "city": CITIES[origin]["name"],
            "distance_km": round(origin_snap_km),
            "note": f"~{round(origin_snap_km)} km from {origin_display} to {CITIES[origin]['name']} (local transport/car)",
        }
        if origin_snap_km > 20
        else None
    )
    last_mile_destination = (
        {
            "city": CITIES[destination]["name"],
            "distance_km": round(destination_snap_km),
            "note": f"~{round(destination_snap_km)} km from {CITIES[destination]['name']} to {destination_display} (local transport/car)",
        }
        if destination_snap_km > 20
        else None
    )

    return {
        "origin":             origin,
        "destination":        destination,
        "origin_name":        origin_display or CITIES[origin]["name"],
        "destination_name":   destination_display or CITIES[destination]["name"],
        "origin_hub":         CITIES[origin]["name"],
        "destination_hub":    CITIES[destination]["name"],
        "last_mile_origin":      last_mile_origin,
        "last_mile_destination": last_mile_destination,
        "routes": {
            "fastest":  enrich(fast,  "Fastest"),
            "cheapest": enrich(cheap, "Cheapest"),
            "greenest": enrich(green, "Greenest"),
        },
    }
