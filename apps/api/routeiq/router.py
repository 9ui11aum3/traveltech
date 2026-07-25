"""Dijkstra-based multimodal route finder."""
import heapq
from typing import Optional
from .data import GRAPH, CITIES


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


def find_routes(origin: str, destination: str) -> dict:
    if origin not in CITIES or destination not in CITIES:
        return {"error": "unknown_city"}
    if origin == destination:
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
                    "from":     s["from"],
                    "from_name": CITIES[s["from"]]["name"],
                    "to":       s["to"],
                    "to_name":  CITIES[s["to"]]["name"],
                    "mode":     s["mode"],
                    "operator": s["operator"],
                    "duration": s["duration"],
                    "price":    s["price"],
                    "co2":      s["co2"],
                }
                for s in segs
            ],
        }

    return {
        "origin":      origin,
        "destination": destination,
        "origin_name":      CITIES[origin]["name"],
        "destination_name": CITIES[destination]["name"],
        "routes": {
            "fastest": enrich(fast,  "Fastest"),
            "cheapest": enrich(cheap, "Cheapest"),
            "greenest": enrich(green, "Greenest"),
        },
    }
