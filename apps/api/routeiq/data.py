"""Static route graph — 25 European cities, 55+ routes."""

CITIES = {
    "amsterdam":  {"name": "Amsterdam",  "country": "Netherlands", "lat": 52.3676, "lon": 4.9041},
    "barcelona":  {"name": "Barcelona",  "country": "Spain",       "lat": 41.3851, "lon": 2.1734},
    "berlin":     {"name": "Berlin",     "country": "Germany",     "lat": 52.5200, "lon": 13.4050},
    "bordeaux":   {"name": "Bordeaux",   "country": "France",      "lat": 44.8378, "lon": -0.5792},
    "brussels":   {"name": "Brussels",   "country": "Belgium",     "lat": 50.8503, "lon": 4.3517},
    "cologne":    {"name": "Cologne",    "country": "Germany",     "lat": 50.9333, "lon": 6.9500},
    "frankfurt":  {"name": "Frankfurt",  "country": "Germany",     "lat": 50.1109, "lon": 8.6821},
    "geneva":     {"name": "Geneva",     "country": "Switzerland", "lat": 46.2044, "lon": 6.1432},
    "hamburg":    {"name": "Hamburg",    "country": "Germany",     "lat": 53.5753, "lon": 10.0153},
    "lille":      {"name": "Lille",      "country": "France",      "lat": 50.6292, "lon": 3.0573},
    "lisbon":     {"name": "Lisbon",     "country": "Portugal",    "lat": 38.7223, "lon": -9.1393},
    "london":     {"name": "London",     "country": "UK",          "lat": 51.5074, "lon": -0.1278},
    "lyon":       {"name": "Lyon",       "country": "France",      "lat": 45.7578, "lon": 4.8320},
    "madrid":     {"name": "Madrid",     "country": "Spain",       "lat": 40.4168, "lon": -3.7038},
    "marseille":  {"name": "Marseille",  "country": "France",      "lat": 43.2965, "lon": 5.3698},
    "milan":      {"name": "Milan",      "country": "Italy",       "lat": 45.4654, "lon": 9.1859},
    "munich":     {"name": "Munich",     "country": "Germany",     "lat": 48.1351, "lon": 11.5820},
    "nice":       {"name": "Nice",       "country": "France",      "lat": 43.7102, "lon": 7.2620},
    "paris":      {"name": "Paris",      "country": "France",      "lat": 48.8566, "lon": 2.3522},
    "prague":     {"name": "Prague",     "country": "Czech Rep.",  "lat": 50.0755, "lon": 14.4378},
    "rome":       {"name": "Rome",       "country": "Italy",       "lat": 41.9028, "lon": 12.4964},
    "strasbourg": {"name": "Strasbourg", "country": "France",      "lat": 48.5734, "lon": 7.7521},
    "toulouse":   {"name": "Toulouse",   "country": "France",      "lat": 43.6047, "lon": 1.4442},
    "vienna":     {"name": "Vienna",     "country": "Austria",     "lat": 48.2082, "lon": 16.3738},
    "zurich":     {"name": "Zurich",     "country": "Switzerland", "lat": 47.3769, "lon": 8.5417},
}

# [from, to, mode, operator, duration_min, price_eur, co2_kg]
ROUTES_RAW = [
    # France domestic – train
    ["paris", "lyon",        "train", "TGV SNCF",     120,  55,   0.8],
    ["paris", "marseille",   "train", "TGV SNCF",     195,  65,   1.5],
    ["paris", "bordeaux",    "train", "TGV SNCF",     210,  55,   1.2],
    ["paris", "toulouse",    "train", "TGV SNCF",     305,  65,   1.4],
    ["paris", "strasbourg",  "train", "TGV SNCF",     110,  38,   1.0],
    ["paris", "lille",       "train", "TGV SNCF",      60,  28,   0.4],
    ["paris", "nice",        "train", "TGV SNCF",     335,  82,   1.9],
    ["lyon",  "marseille",   "train", "TGV SNCF",     105,  35,   0.7],
    ["lyon",  "nice",        "train", "TGV SNCF",     225,  48,   0.9],
    ["lyon",  "barcelona",   "train", "TGV SNCF",     250,  58,   1.3],
    ["lyon",  "geneva",      "train", "TGV SNCF",     120,  32,   0.3],
    ["marseille", "nice",    "train", "TER SNCF",     145,  28,   2.1],
    ["bordeaux", "toulouse", "train", "TGV SNCF",     130,  30,   0.5],
    ["toulouse", "barcelona","train", "TGV SNCF",     210,  42,   1.1],
    ["toulouse", "marseille","train", "TGV SNCF",     200,  45,   0.8],
    ["lille",  "brussels",   "train", "Eurostar",      38,  22,   0.5],
    ["strasbourg", "zurich", "train", "TGV SNCF",     130,  38,   0.3],
    # France domestic – bus
    ["paris", "lyon",        "bus",   "Flixbus",      480,  22,  11.2],
    ["paris", "brussels",    "bus",   "Flixbus",      200,  18,   8.1],
    ["paris", "amsterdam",   "bus",   "Flixbus",      360,  22,  11.6],
    ["paris", "marseille",   "bus",   "Flixbus",      600,  28,  21.6],
    # Cross-border train
    ["paris", "brussels",    "train", "Thalys",        82,  62,   0.9],
    ["paris", "london",      "train", "Eurostar",     140,  88,   1.4],
    ["paris", "frankfurt",   "train", "TGV/ICE",      230,  88,   2.3],
    ["strasbourg", "frankfurt", "train", "ICE DB",     60,  26,   1.1],
    ["nice",  "milan",       "train", "Thello",       315,  55,   1.2],
    ["bordeaux", "lisbon",   "bus",   "Flixbus",      600,  52,  21.0],
    # Benelux
    ["brussels", "amsterdam","train", "Thalys",       109,  38,   0.8],
    ["brussels", "cologne",  "train", "ICE DB",       111,  42,   1.1],
    ["brussels", "london",   "train", "Eurostar",     120,  78,   1.1],
    ["amsterdam", "cologne", "train", "ICE DB",       155,  48,   1.6],
    ["amsterdam", "hamburg", "train", "ICE DB",       220,  65,   2.8],
    # Germany
    ["cologne",  "frankfurt","train", "ICE DB",        65,  32,   1.1],
    ["frankfurt","berlin",   "train", "ICE DB",       235,  78,   3.3],
    ["frankfurt","munich",   "train", "ICE DB",       195,  68,   2.4],
    ["frankfurt","zurich",   "train", "ICE DB",       240,  72,   2.2],
    ["berlin",   "hamburg",  "train", "ICE DB",       105,  48,   1.7],
    ["berlin",   "munich",   "train", "ICE DB",       280,  82,   3.5],
    ["berlin",   "prague",   "train", "EC",           280,  58,   2.1],
    ["berlin",   "hamburg",  "bus",   "Flixbus",      200,  15,   8.1],
    ["munich",   "vienna",   "train", "RailJet",      155,  52,   2.6],
    ["munich",   "zurich",   "train", "EC",           195,  62,   1.9],
    ["munich",   "milan",    "train", "EC",           330,  78,   4.1],
    ["munich",   "prague",   "train", "EC",           320,  68,   3.2],
    # Switzerland / Austria
    ["zurich",   "milan",    "train", "SBB",          210,  62,   0.6],
    ["zurich",   "vienna",   "train", "NightJet",     390,  88,   2.3],
    ["zurich",   "munich",   "train", "EC",           195,  62,   1.9],
    ["geneva",   "milan",    "train", "EC",           240,  65,   0.7],
    ["geneva",   "marseille","train", "TGV SNCF",     300,  58,   0.9],
    ["vienna",   "prague",   "train", "RailJet",      240,  58,   2.0],
    ["vienna",   "berlin",   "train", "NightJet",     570,  85,   3.4],
    # Italy
    ["milan",    "rome",     "train", "Frecciarossa", 185,  72,   1.6],
    # Spain
    ["barcelona","madrid",   "train", "AVE Renfe",    155,  62,   1.9],
    ["barcelona","madrid",   "bus",   "Alsa",         370,  28,  17.5],
    ["madrid",   "lisbon",   "train", "Trenhotel",    640,  52,   3.8],
    # Flights
    ["paris",    "berlin",   "plane", "Air France",   155, 148,  52.0],
    ["paris",    "madrid",   "plane", "Iberia",       135, 118,  50.0],
    ["paris",    "rome",     "plane", "Air France",   140, 128,  53.0],
    ["london",   "paris",    "plane", "British Airways", 100, 135, 40.0],
    ["london",   "barcelona","plane", "easyJet",      155,  95, 105.0],
    ["amsterdam","berlin",   "plane", "KLM",           90,  98,  35.0],
    ["amsterdam","london",   "plane", "KLM",           65,  92,  32.0],
    ["barcelona","rome",     "plane", "Vueling",      130,  88,  72.0],
    ["munich",   "rome",     "plane", "Lufthansa",    110,  95,  56.0],
    ["berlin",   "lisbon",   "plane", "TAP Air",      230, 165, 105.0],
]


def build_graph() -> dict:
    graph: dict = {}
    for row in ROUTES_RAW:
        frm, to, mode, operator, duration, price, co2 = row
        edge = {"mode": mode, "operator": operator, "duration": duration, "price": price, "co2": co2}
        graph.setdefault(frm, []).append({"to": to, "from": frm, **edge})
        graph.setdefault(to,  []).append({"to": frm, "from": to, **edge})
    return graph


GRAPH = build_graph()
