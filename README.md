# RouteIQ — Multimodal Travel Intelligence

> Europe's smartest travel router: compare time, cost, and carbon footprint across train, bus, and flight.

[![API](https://img.shields.io/badge/API-FastAPI-009688?logo=fastapi)](https://routeiq-api.app.syit.fr/docs)
[![Frontend](https://img.shields.io/badge/Frontend-React%20%2B%20Vite-61dafb?logo=react)](https://routeiq.app.syit.fr)

---

## What it does

RouteIQ takes an origin and a destination (25 European cities) and returns three routes:

| Route | Optimisation |
|-------|-------------|
| **Fastest** | Minimize total travel time (Dijkstra on duration graph) |
| **Cheapest** | Minimize total ticket price |
| **Greenest** | Minimize CO₂ emissions |

Each route shows: segments (operator, mode, duration, price), total CO₂, and a live OpenStreetMap overlay. A carbon comparison bar benchmarks against car and estimated flight.

An **onboarding wizard** captures home city, travel style, and carbon sensitivity — stored via the REST API.

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Browser                          │
│  React + Vite SPA (routeiq.app.syit.fr)             │
│  - Search UI (From/To/Date)                         │
│  - Route cards (Fastest / Cheapest / Greenest)      │
│  - Leaflet map overlay                              │
│  - CO₂ comparison chart                            │
│  - Onboarding wizard (3-step preferences modal)     │
└──────────────────────┬──────────────────────────────┘
                       │ /api/* (nginx proxy)
┌──────────────────────▼──────────────────────────────┐
│              FastAPI Backend                         │
│  (routeiq-api.app.syit.fr)                          │
│                                                     │
│  GET  /routes?from=paris&to=berlin                  │
│  GET  /cities                                       │
│  POST /onboarding                                   │
│  GET  /onboarding/{email}                           │
│  GET  /health                                       │
│                                                     │
│  ┌──────────────┐  ┌──────────────────────────────┐ │
│  │ Route Engine │  │  SQLite (user preferences)   │ │
│  │ Dijkstra on  │  │  email / home_city /          │ │
│  │ 25-city graph│  │  travel_style / co2 sens.    │ │
│  └──────────────┘  └──────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

### Data sources (free, open)

| Source | Usage |
|--------|-------|
| Static 25-city European graph (55+ routes) | Route search core |
| OpenStreetMap (Leaflet tiles) | Map overlay |
| Hardcoded CO₂ factors (ADEME methodology) | CO₂ comparison |

---

## Repository layout

```
traveltech/
├── apps/
│   ├── api/              FastAPI backend
│   │   ├── main.py       API entrypoint + endpoints
│   │   ├── routeiq/
│   │   │   ├── data.py   25-city graph + 55 routes
│   │   │   └── router.py Dijkstra route finder
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   └── web/              React + Vite frontend
│       ├── src/
│       │   ├── App.jsx
│       │   ├── api.js    API client
│       │   └── components/
│       │       ├── RouteCard.jsx
│       │       ├── Co2Chart.jsx
│       │       ├── RouteMap.jsx
│       │       └── OnboardingModal.jsx
│       ├── Dockerfile
│       └── nginx.conf
├── docker-compose.yml    Local dev + production
└── README.md
```

---

## Running locally

**Prerequisites**: Docker + Docker Compose

```bash
git clone git@github.com:9ui11aum3/traveltech.git
cd traveltech
docker compose up --build
```

- Frontend: http://localhost
- API docs: http://localhost:8000/docs

---

## API reference

### GET /routes

```
GET /routes?from=paris&to=berlin
```

Response:
```json
{
  "origin": "paris",
  "destination": "berlin",
  "origin_name": "Paris",
  "destination_name": "Berlin",
  "routes": {
    "fastest":  { "label": "Fastest",  "total_duration": 395, "total_price": 166, "total_co2": 3.2, "transfers": 1, "segments": [...] },
    "cheapest": { ... },
    "greenest": { ... }
  }
}
```

### POST /onboarding

```json
{
  "email": "user@example.com",
  "home_city": "paris",
  "travel_style": "balanced",
  "carbon_sensitivity": "medium"
}
```

`travel_style` values: `fast | cheap | green | balanced`  
`carbon_sensitivity` values: `low | medium | high`

---

## Deployment (AK3S)

Deployed via docker-compose on AK3S (Kubernetes-based PaaS).

- Frontend: https://routeiq.app.syit.fr
- API: https://routeiq-api.app.syit.fr
- API docs: https://routeiq-api.app.syit.fr/docs

Resources: 1 replica per service, 256MB RAM limit (API), 128MB (web).

---

## Tech stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Backend | FastAPI (Python 3.12) | Fast async, auto OpenAPI docs, lightweight |
| Route engine | Dijkstra (stdlib heapq) | No dependencies, correct for static graphs |
| Storage | SQLite | Zero infra, sufficient for prototype |
| Frontend | React 18 + Vite | Fast builds, modern DX |
| Map | Leaflet + OpenStreetMap | Free, no API key required |
| Container | Docker + nginx | Single compose file, reproducible |

---

*RouteIQ — For investor demonstration. Open data only.*
