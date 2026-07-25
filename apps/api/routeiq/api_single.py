"""RouteIQ API — single-file version for AK3S deployment."""
import heapq, os, sqlite3
from contextlib import asynccontextmanager
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

app = FastAPI(title="RouteIQ API", version="0.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/routes")
def routes(from_city:str=Query(...,alias="from"), to:str=Query(...)):
    origin,dest = from_city.lower(), to.lower()
    if origin not in CITIES or dest not in CITIES:
        raise HTTPException(404,"unknown_city")
    if origin == dest:
        raise HTTPException(400,"same_city")
    def enrich(route, label):
        if not route: return None
        s = route["segments"]
        return {"label":label,"total_duration":sum(x["duration"] for x in s),"total_price":sum(x["price"] for x in s),"total_co2":round(sum(x["co2"] for x in s),2),"transfers":max(0,len(s)-1),"segments":[{"from":x["from"],"from_name":CITIES[x["from"]]["name"],"to":x["to"],"to_name":CITIES[x["to"]]["name"],"mode":x["mode"],"operator":x["operator"],"duration":x["duration"],"price":x["price"],"co2":x["co2"]} for x in s]}
    return {"origin":origin,"destination":dest,"origin_name":CITIES[origin]["name"],"destination_name":CITIES[dest]["name"],"routes":{"fastest":enrich(dijkstra(origin,dest,"duration"),"Fastest"),"cheapest":enrich(dijkstra(origin,dest,"price"),"Cheapest"),"greenest":enrich(dijkstra(origin,dest,"co2"),"Greenest")}}

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
def health(): return {"status":"ok","version":"0.1.0"}
