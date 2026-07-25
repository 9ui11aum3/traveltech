"""RouteIQ API — single-file version for AK3S deployment."""
import heapq, math, os, sqlite3
from contextlib import asynccontextmanager
from typing import Optional
import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

CITIES = {
    "amsterdam":  {"name":"Amsterdam",  "country":"Netherlands","lat":52.3676,"lon":4.9041},
    "barcelona":  {"name":"Barcelona",  "country":"Spain",      "lat":41.3851,"lon":2.1734},
    "berlin":     {"name":"Berlin",     "country":"Germany",    "lat":52.5200,"lon":13.4050},
    "bordeaux":   {"name":"Bordeaux",   "country":"France",     "lat":44.8378,"lon":-0.5792},
    "brussels":   {"name":"Brussels",   "country":"Belgium",    "lat":50.8503,"lon":4.3517},
    "cologne":    {"name":"Cologne",    "country":"Germany",    "lat":50.9333,"lon":6.9500},
    "frankfurt":  {"name":"Frankfurt",  "country":"Germany",    "lat":50.1109,"lon":8.6821},
    "geneva":     {"name":"Geneva",     "country":"Switzerland","lat":46.2044,"lon":6.1432},
    "hamburg":    {"name":"Hamburg",    "country":"Germany",    "lat":53.5753,"lon":10.0153},
    "lille":      {"name":"Lille",      "country":"France",     "lat":50.6292,"lon":3.0573},
    "lisbon":     {"name":"Lisbon",     "country":"Portugal",   "lat":38.7223,"lon":-9.1393},
    "london":     {"name":"London",     "country":"UK",         "lat":51.5074,"lon":-0.1278},
    "lyon":       {"name":"Lyon",       "country":"France",     "lat":45.7578,"lon":4.8320},
    "madrid":     {"name":"Madrid",     "country":"Spain",      "lat":40.4168,"lon":-3.7038},
    "marseille":  {"name":"Marseille",  "country":"France",     "lat":43.2965,"lon":5.3698},
    "milan":      {"name":"Milan",      "country":"Italy",      "lat":45.4654,"lon":9.1859},
    "munich":     {"name":"Munich",     "country":"Germany",    "lat":48.1351,"lon":11.5820},
    "nice":       {"name":"Nice",       "country":"France",     "lat":43.7102,"lon":7.2620},
    "paris":      {"name":"Paris",      "country":"France",     "lat":48.8566,"lon":2.3522},
    "prague":     {"name":"Prague",     "country":"Czech Rep.", "lat":50.0755,"lon":14.4378},
    "rome":       {"name":"Rome",       "country":"Italy",      "lat":41.9028,"lon":12.4964},
    "strasbourg": {"name":"Strasbourg", "country":"France",     "lat":48.5734,"lon":7.7521},
    "toulouse":   {"name":"Toulouse",   "country":"France",     "lat":43.6047,"lon":1.4442},
    "vienna":     {"name":"Vienna",     "country":"Austria",    "lat":48.2082,"lon":16.3738},
    "zurich":     {"name":"Zurich",     "country":"Switzerland","lat":47.3769,"lon":8.5417},
}

ROUTES_RAW = [
    ["paris","lyon","train","TGV SNCF",120,55,0.8],["paris","marseille","train","TGV SNCF",195,65,1.5],
    ["paris","bordeaux","train","TGV SNCF",210,55,1.2],["paris","toulouse","train","TGV SNCF",305,65,1.4],
    ["paris","strasbourg","train","TGV SNCF",110,38,1.0],["paris","lille","train","TGV SNCF",60,28,0.4],
    ["paris","nice","train","TGV SNCF",335,82,1.9],["lyon","marseille","train","TGV SNCF",105,35,0.7],
    ["lyon","nice","train","TGV SNCF",225,48,0.9],["lyon","barcelona","train","TGV SNCF",250,58,1.3],
    ["lyon","geneva","train","TGV SNCF",120,32,0.3],["marseille","nice","train","TER SNCF",145,28,2.1],
    ["bordeaux","toulouse","train","TGV SNCF",130,30,0.5],["toulouse","barcelona","train","TGV SNCF",210,42,1.1],
    ["toulouse","marseille","train","TGV SNCF",200,45,0.8],["lille","brussels","train","Eurostar",38,22,0.5],
    ["strasbourg","zurich","train","TGV SNCF",130,38,0.3],["paris","lyon","bus","Flixbus",480,22,11.2],
    ["paris","brussels","bus","Flixbus",200,18,8.1],["paris","amsterdam","bus","Flixbus",360,22,11.6],
    ["paris","marseille","bus","Flixbus",600,28,21.6],["paris","brussels","train","Thalys",82,62,0.9],
    ["paris","london","train","Eurostar",140,88,1.4],["paris","frankfurt","train","TGV/ICE",230,88,2.3],
    ["strasbourg","frankfurt","train","ICE DB",60,26,1.1],["nice","milan","train","Thello",315,55,1.2],
    ["bordeaux","lisbon","bus","Flixbus",600,52,21.0],["brussels","amsterdam","train","Thalys",109,38,0.8],
    ["brussels","cologne","train","ICE DB",111,42,1.1],["brussels","london","train","Eurostar",120,78,1.1],
    ["amsterdam","cologne","train","ICE DB",155,48,1.6],["amsterdam","hamburg","train","ICE DB",220,65,2.8],
    ["cologne","frankfurt","train","ICE DB",65,32,1.1],["frankfurt","berlin","train","ICE DB",235,78,3.3],
    ["frankfurt","munich","train","ICE DB",195,68,2.4],["frankfurt","zurich","train","ICE DB",240,72,2.2],
    ["berlin","hamburg","train","ICE DB",105,48,1.7],["berlin","munich","train","ICE DB",280,82,3.5],
    ["berlin","prague","train","EC",280,58,2.1],["berlin","hamburg","bus","Flixbus",200,15,8.1],
    ["munich","vienna","train","RailJet",155,52,2.6],["munich","zurich","train","EC",195,62,1.9],
    ["munich","milan","train","EC",330,78,4.1],["munich","prague","train","EC",320,68,3.2],
    ["zurich","milan","train","SBB",210,62,0.6],["zurich","vienna","train","NightJet",390,88,2.3],
    ["zurich","munich","train","EC",195,62,1.9],["geneva","milan","train","EC",240,65,0.7],
    ["geneva","marseille","train","TGV SNCF",300,58,0.9],["vienna","prague","train","RailJet",240,58,2.0],
    ["vienna","berlin","train","NightJet",570,85,3.4],["milan","rome","train","Frecciarossa",185,72,1.6],
    ["barcelona","madrid","train","AVE Renfe",155,62,1.9],["barcelona","madrid","bus","Alsa",370,28,17.5],
    ["madrid","lisbon","train","Trenhotel",640,52,3.8],["paris","berlin","plane","Air France",155,148,52.0],
    ["paris","madrid","plane","Iberia",135,118,50.0],["paris","rome","plane","Air France",140,128,53.0],
    ["london","paris","plane","British Airways",100,135,40.0],["london","barcelona","plane","easyJet",155,95,105.0],
    ["amsterdam","berlin","plane","KLM",90,98,35.0],["amsterdam","london","plane","KLM",65,92,32.0],
    ["barcelona","rome","plane","Vueling",130,88,72.0],["munich","rome","plane","Lufthansa",110,95,56.0],
    ["berlin","lisbon","plane","TAP Air",230,165,105.0],
]

def build_graph():
    g = {}
    for row in ROUTES_RAW:
        frm,to,mode,op,dur,price,co2 = row
        edge = {"mode":mode,"operator":op,"duration":dur,"price":price,"co2":co2}
        g.setdefault(frm,[]).append({"to":to,"from":frm,**edge})
        g.setdefault(to, []).append({"to":frm,"from":to,**edge})
    return g

GRAPH = build_graph()

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))

def snap_to_nearest(lat, lon):
    best_key, best_dist = "", float("inf")
    for key, city in CITIES.items():
        d = haversine_km(lat, lon, city["lat"], city["lon"])
        if d < best_dist:
            best_dist = d
            best_key = key
    return best_key, best_dist

def dijkstra(source, target, wkey):
    dist = {source: 0.0}; prev = {}; pq = [(0.0, source)]
    while pq:
        cost, u = heapq.heappop(pq)
        if cost > dist.get(u, float("inf")): continue
        if u == target: break
        for edge in GRAPH.get(u, []):
            nc = cost + edge[wkey]
            if nc < dist.get(edge["to"], float("inf")):
                dist[edge["to"]] = nc
                prev[edge["to"]] = {"node":u,"edge":edge}
                heapq.heappush(pq,(nc,edge["to"]))
    if target not in dist: return None
    segs = []; n = target
    while n in prev:
        e = prev[n]; segs.insert(0,{**e["edge"],"from":e["node"],"to":n}); n = e["node"]
    return {"total":dist[target],"segments":segs}

DB_PATH = os.getenv("DB_PATH","/data/routeiq.db")

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE NOT NULL, home_city TEXT NOT NULL, travel_style TEXT NOT NULL DEFAULT 'balanced', carbon_sensitivity TEXT NOT NULL DEFAULT 'medium', created_at DATETIME DEFAULT CURRENT_TIMESTAMP)")
    conn.commit(); conn.close()

@asynccontextmanager
async def lifespan(app):
    init_db(); yield

app = FastAPI(title="RouteIQ API", version="0.2.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/geocode")
async def geocode(q: str = Query(..., min_length=2)):
    CITY_TYPES = {"city","town","village","municipality","borough","suburb","district"}
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get("https://photon.komoot.io/api/", params={"q":q,"limit":10,"lang":"en"})
        features = resp.json().get("features",[])
    except Exception:
        features = []
    results = []; seen = set()
    for f in features:
        p = f.get("properties",{})
        if p.get("osm_type")=="R" or p.get("type") in CITY_TYPES or p.get("osm_key")=="place":
            name = p.get("name",""); country = p.get("country","")
            key = (name.lower(), country.lower())
            if key in seen or not name: continue
            seen.add(key)
            results.append({"name":name,"country":country,"state":p.get("state",""),"lat":f["geometry"]["coordinates"][1],"lon":f["geometry"]["coordinates"][0]})
        if len(results) >= 6: break
    return results

@app.get("/snap")
def snap(lat: float = Query(...), lon: float = Query(...)):
    slug, dist_km = snap_to_nearest(lat, lon)
    city = CITIES[slug]
    return {"slug":slug,"name":city["name"],"country":city["country"],"distance_km":round(dist_km)}

@app.get("/routes")
def routes(
    from_city: Optional[str] = Query(None, alias="from"),
    to: Optional[str] = Query(None),
    from_lat: Optional[float] = Query(None),
    from_lon: Optional[float] = Query(None),
    to_lat: Optional[float] = Query(None),
    to_lon: Optional[float] = Query(None),
    from_name: Optional[str] = Query(None),
    to_name: Optional[str] = Query(None),
):
    if from_lat is not None and from_lon is not None:
        origin_slug, origin_snap_km = snap_to_nearest(from_lat, from_lon)
        origin_display = from_name or origin_slug
    elif from_city:
        origin_slug = from_city.lower(); origin_snap_km = 0.0
        origin_display = from_name or CITIES.get(origin_slug,{}).get("name",origin_slug)
    else:
        raise HTTPException(400,"Provide 'from' or 'from_lat'+'from_lon'")

    if to_lat is not None and to_lon is not None:
        dest_slug, dest_snap_km = snap_to_nearest(to_lat, to_lon)
        dest_display = to_name or dest_slug
    elif to:
        dest_slug = to.lower(); dest_snap_km = 0.0
        dest_display = to_name or CITIES.get(dest_slug,{}).get("name",dest_slug)
    else:
        raise HTTPException(400,"Provide 'to' or 'to_lat'+'to_lon'")

    if origin_slug not in CITIES or dest_slug not in CITIES:
        raise HTTPException(404,"unknown_city")
    if origin_slug == dest_slug and origin_snap_km < 1 and dest_snap_km < 1:
        raise HTTPException(400,"same_city")

    def enrich(route, label):
        if not route: return None
        s = route["segments"]
        return {
            "label":label,
            "total_duration":sum(x["duration"] for x in s),
            "total_price":sum(x["price"] for x in s),
            "total_co2":round(sum(x["co2"] for x in s),2),
            "transfers":max(0,len(s)-1),
            "segments":[{
                "from":x["from"],"from_name":CITIES[x["from"]]["name"],
                "from_lat":CITIES[x["from"]]["lat"],"from_lon":CITIES[x["from"]]["lon"],
                "to":x["to"],"to_name":CITIES[x["to"]]["name"],
                "to_lat":CITIES[x["to"]]["lat"],"to_lon":CITIES[x["to"]]["lon"],
                "mode":x["mode"],"operator":x["operator"],"duration":x["duration"],"price":x["price"],"co2":x["co2"]
            } for x in s]
        }

    last_mile_origin = {"city":CITIES[origin_slug]["name"],"distance_km":round(origin_snap_km),"note":f"~{round(origin_snap_km)} km from {origin_display} to {CITIES[origin_slug]['name']} (local transport/car)"} if origin_snap_km > 20 else None
    last_mile_dest = {"city":CITIES[dest_slug]["name"],"distance_km":round(dest_snap_km),"note":f"~{round(dest_snap_km)} km from {CITIES[dest_slug]['name']} to {dest_display} (local transport/car)"} if dest_snap_km > 20 else None

    return {
        "origin":origin_slug,"destination":dest_slug,
        "origin_name":origin_display,"destination_name":dest_display,
        "origin_hub":CITIES[origin_slug]["name"],"destination_hub":CITIES[dest_slug]["name"],
        "last_mile_origin":last_mile_origin,"last_mile_destination":last_mile_dest,
        "routes":{"fastest":enrich(dijkstra(origin_slug,dest_slug,"duration"),"Fastest"),"cheapest":enrich(dijkstra(origin_slug,dest_slug,"price"),"Cheapest"),"greenest":enrich(dijkstra(origin_slug,dest_slug,"co2"),"Greenest")}
    }

@app.get("/cities")
def cities():
    return [{"id":k,"name":v["name"],"country":v["country"],"lat":v["lat"],"lon":v["lon"]} for k,v in sorted(CITIES.items(),key=lambda x:x[1]["name"])]

class UserPreferences(BaseModel):
    email:str; home_city:str; travel_style:str="balanced"; carbon_sensitivity:str="medium"

@app.post("/onboarding",status_code=201)
def onboarding(p:UserPreferences):
    if p.home_city not in CITIES: raise HTTPException(400,"unknown_home_city")
    if p.travel_style not in {"fast","cheap","green","balanced"}: raise HTTPException(400,"invalid_travel_style")
    if p.carbon_sensitivity not in {"low","medium","high"}: raise HTTPException(400,"invalid_carbon_sensitivity")
    conn = sqlite3.connect(DB_PATH)
    try: conn.execute("INSERT OR REPLACE INTO users (email,home_city,travel_style,carbon_sensitivity) VALUES (?,?,?,?)",(p.email,p.home_city,p.travel_style,p.carbon_sensitivity)); conn.commit()
    finally: conn.close()
    return {"status":"ok","home_city":p.home_city}

@app.get("/onboarding/{email}")
def get_prefs(email:str):
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute("SELECT email,home_city,travel_style,carbon_sensitivity FROM users WHERE email=?",(email,)).fetchone(); conn.close()
    if not row: raise HTTPException(404,"user_not_found")
    return {"email":row[0],"home_city":row[1],"travel_style":row[2],"carbon_sensitivity":row[3]}

@app.get("/health")
def health(): return {"status":"ok","version":"0.2.0"}
