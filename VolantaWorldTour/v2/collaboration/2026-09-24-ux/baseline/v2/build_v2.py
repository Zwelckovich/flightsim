"""Baut die Weltreise V2 aus route.json + content.json.

Ausgaben:
  ../Volanta-Worldtour-V2.html   vollständiges, offline nutzbares HTML
  dist/artifact.html             dieselbe Seite als Artifact-Fragment (d3 per CDN)
  tour-v2.json                   alle berechneten Daten (Legs, Airports, Kategorien)

Aufruf:  python v2/build_v2.py
"""
import csv
import datetime
import json
import math
import os
import pathlib
import re
import sys
from collections import defaultdict

V2 = pathlib.Path(__file__).resolve().parent
ROOT = V2.parent
WORK = ROOT / "work"


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


route = load_json(V2 / "route.json")
# Für Tests lassen sich andere Inhalte und ein anderes Archiv übergeben (siehe tests/).
content = load_json(pathlib.Path(os.environ.get("WELTREISE_CONTENT", V2 / "content.json")))
v1 = load_json(WORK / "tour-data.json")
v1x = load_json(WORK / "excursions.json")
debrief_path = pathlib.Path(os.environ.get("WELTREISE_DEBRIEFS", V2 / "debriefings.json"))
debriefs = load_json(debrief_path) if debrief_path.exists() else {"entries": []}

with open(WORK / "airports.csv", encoding="utf-8") as f:
    OA = {r["ident"]: r for r in csv.DictReader(f)}
# Einige Flughäfen führen in OurAirports noch ihre alte Kennung (z. B. SPIM statt SPJC).
OA_BY_CODE = {}
for r in OA.values():
    for code in (r["icao_code"], r["gps_code"]):
        if code and code not in OA:
            OA_BY_CODE.setdefault(code, r)
RUNWAYS = defaultdict(list)
with open(WORK / "runways.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        if r["closed"] != "1":
            RUNWAYS[r["airport_ident"]].append(r)
with open(ROOT / "MSFS Airports - Addons.csv", encoding="utf-8-sig") as f:
    OWNED = {r["ICAO"].strip(): r for r in csv.DictReader(f) if r["ICAO"].strip()}

CATEGORY_NAMES = {c["code"]: c["name"] for c in v1["countries"]}
if len(CATEGORY_NAMES) != 245:
    sys.exit(f"Erwartet 245 Volanta-Kategorien, gefunden {len(CATEGORY_NAMES)}")

# Volanta ordnet diese Regionen eigenen Kategorien zu; OurAirports führt sie unter FI/NO.
REGION_TO_CATEGORY = {"FI-01": "AX", "NO-21": "SJ", "NO-22": "SJ"}


def oa_row(ident):
    return OA.get(ident) or OA_BY_CODE.get(ident)


def country_of(ident):
    if ident in v1["airports"] and v1["airports"][ident].get("country"):
        return v1["airports"][ident]["country"]
    row = oa_row(ident)
    if not row:
        return None
    return REGION_TO_CATEGORY.get(row["iso_region"], row["iso_country"])


PAVED = ("ASP", "CON", "PEM", "BIT", "TAR", "ASPHALT", "CONCRETE")


def is_paved(surface):
    s = (surface or "").strip().upper()
    return any(s.startswith(p) for p in PAVED)


def main_runway(ident):
    """Längste befestigte Bahn; nur ohne befestigte Bahn die längste insgesamt (z. B. Eis, Gras)."""
    candidates = []
    for r in RUNWAYS.get(ident, []):
        try:
            length_m = round(int(r["length_ft"]) * 0.3048)
        except ValueError:
            continue
        width = r["width_ft"]
        candidates.append({
            "id": "/".join(x for x in (r["le_ident"], r["he_ident"]) if x),
            "m": length_m,
            "w": round(int(width) * 0.3048) if width.isdigit() else None,
            "s": (r["surface"] or "").upper()[:10],
            "paved": is_paved(r["surface"]),
        })
    if not candidates:
        return None
    paved = [c for c in candidates if c["paved"]]
    best = max(paved or candidates, key=lambda c: c["m"])
    best.pop("paved")
    return best


def airport_record(ident):
    row = oa_row(ident)
    if row is None:
        sys.exit(f"Airport {ident} nicht in OurAirports gefunden")
    if row["type"] == "closed":
        sys.exit(f"Airport {ident} ist geschlossen – V2 nutzt nur aktive Plätze")
    cc = country_of(ident)
    if cc not in CATEGORY_NAMES:
        sys.exit(f"Kategorie {cc} für {ident} unbekannt")
    elev = row["elevation_ft"]
    return {
        "i": ident,
        "n": row["name"],
        "c": row["municipality"] or "",
        "cc": cc,
        "lat": round(float(row["latitude_deg"]), 5),
        "lon": round(float(row["longitude_deg"]), 5),
        "el": int(float(elev)) if elev not in ("", None) else None,
        "type": row["type"],
        "rw": main_runway(row["ident"]),
    }


def gc_nm(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a["lat"], a["lon"], b["lat"], b["lon"]))
    c = math.sin(la1) * math.sin(la2) + math.cos(la1) * math.cos(la2) * math.cos(lo2 - lo1)
    return math.degrees(math.acos(max(-1.0, min(1.0, c)))) * 60


def a320_minutes(nm):
    return max(25, round(18 + nm * 1.07 / 430 * 60))


def h160_minutes(nm):
    return round(12 + nm * 1.10 / 138 * 60)


# ---------- Airports ----------
airports = {}


def ensure(ident):
    if ident not in airports:
        airports[ident] = airport_record(ident)
    return airports[ident]


chapters = route["chapters"]
previous_end = None
for ch in chapters:
    seq = ch["route"]
    if previous_end is not None and seq[0] != previous_end:
        sys.exit(f"Kapitel {ch['id']} beginnt bei {seq[0]}, vorheriges endet bei {previous_end}")
    previous_end = seq[-1]
    for ident in seq:
        ensure(ident)
if chapters[0]["route"][0] != route["start"] or chapters[-1]["route"][-1] != route["start"]:
    sys.exit("Die Reise muss in EDLV beginnen und enden")

excursions = {}
for e in route["excursions"]:
    ensure(e["anchor"])
    ensure(e["target"])
    if "fallback" in e:
        ensure(e["fallback"]["anchor"])
        ensure(e["fallback"]["target"])
    text = content["excursions"].get(e["id"])
    if not text:
        sys.exit(f"Kein Ausflugstext für {e['id']}")
    excursions[e["id"]] = {**e, **text, "legs": []}

# ---------- Szenerien ----------
v1_labels = {}
for ident, a in v1["airports"].items():
    if a.get("scenery") == "wu":
        v1_labels[ident] = a["sceneryLabel"]
    elif a.get("scenery") == "base":
        v1_labels[ident] = "Basis-Sim"
hand = {**v1_labels, **content["handcrafted"]}

# Datenvertrag mit app.js: candidate = kostenlose Alternative ohne ausreichende Belege (keine Empfehlung),
# dependencies = zusätzliche Downloads, installNote = Hinweis für die Kapitel-Checkliste,
# simChecks = offene Prüfung, ob ein Landeplatz im Sim existiert (nur "unconfirmed" – bestätigen kann erst ein Test).
ITEM_STATUS = {"buy", "freeware", "optional", "candidate"}
DEP_KEYS = {"product", "dev", "url", "required", "note"}


def is_url(u):
    return isinstance(u, str) and u.startswith("https://")


def filled(s):
    return isinstance(s, str) and bool(s.strip())


def validate_scenery(scenery):
    errors = []
    for key, s in scenery.items():
        where = f"Szenerie {key}"
        st = s.get("status")
        if st not in ITEM_STATUS:
            errors.append(f"{where}: unbekannter Status {st!r}")
            continue
        if not filled(s.get("product")) or not is_url(s.get("url")):
            errors.append(f"{where}: Produkt und https-Link nötig")
        if st == "candidate" and s.get("required"):
            errors.append(f"{where}: ein Kandidat kann keine Pflicht sein")
        deps = s.get("dependencies")
        if deps is not None and (not isinstance(deps, list) or not deps):
            errors.append(f"{where}: dependencies muss eine nicht leere Liste sein")
            deps = []
        for n, d in enumerate(deps or [], 1):
            if not isinstance(d, dict):
                errors.append(f"{where}: Abhängigkeit {n} ist kein Objekt")
                continue
            if set(d) - DEP_KEYS:
                errors.append(f"{where}: Abhängigkeit {n} hat unbekannte Felder {sorted(set(d) - DEP_KEYS)}")
            if not filled(d.get("product")) or not is_url(d.get("url")):
                errors.append(f"{where}: Abhängigkeit {n} braucht Produkt und https-Link")
            if not isinstance(d.get("required"), bool):
                errors.append(f"{where}: Abhängigkeit {n}: required muss true oder false sein")
            for k in ("dev", "note"):
                if k in d and not filled(d[k]):
                    errors.append(f"{where}: Abhängigkeit {n}: {k} ist leer")
        if "installNote" in s and not filled(s["installNote"]):
            errors.append(f"{where}: installNote ist leer")
    return errors


def validate_sim_checks(checks):
    if not isinstance(checks, dict):
        return ["simChecks muss ein Objekt nach ICAO sein"]
    errors = []
    for ident, c in checks.items():
        where = f"simChecks {ident}"
        if ident not in airports:
            errors.append(f"{where}: Landeplatz nicht in der Tour")
        if not isinstance(c, dict):
            errors.append(f"{where}: kein Objekt")
            continue
        if c.get("status") != "unconfirmed":
            errors.append(f"{where}: status muss 'unconfirmed' sein")
        if not filled(c.get("note")):
            errors.append(f"{where}: note fehlt")
        sources = c.get("sources")
        if not isinstance(sources, list) or not sources or not all(is_url(u) for u in sources):
            errors.append(f"{where}: sources braucht mindestens einen https-Link")
    return errors


sim_checks = content.get("simChecks", {})
scenery_errors = validate_scenery(content["scenery"]) + validate_sim_checks(sim_checks)
if scenery_errors:
    sys.exit("Szenerie-Daten ungültig:\n  " + "\n  ".join(scenery_errors))

recommendations = defaultdict(list)
for key, s in content["scenery"].items():
    ident = s.get("icao", key)
    item = {k: v for k, v in s.items() if k != "icao"}
    recommendations[ident].append(item)

# Ein Kandidat steht immer hinter einem Urteil über den Standard (auch hinter "ungeprüft") – nie als Hauptstatus.
PRIORITY = {"owned": 0, "buy": 1, "freeware": 2, "hand": 3, "stdok": 4, "addon": 5, "optional": 6, "unrated": 7,
            "candidate": 8}


def scenery_for(ident):
    items = []
    if ident in OWNED:
        o = OWNED[ident]
        items.append({"status": "owned", "product": o["Name"].strip() or ident,
                      "dev": o["Hersteller"].strip(), "store": o["Store"].strip(),
                      "note": content["ownedNotes"].get(ident)})
    for rec in recommendations.get(ident, []):
        items.append(dict(rec))
    if ident in hand:
        items.append({"status": "hand", "product": hand[ident]})
    if ident in content.get("defaultOk", {}):
        items.append({"status": "stdok", "why": content["defaultOk"][ident]})
    if not any(it["status"] in ("owned", "buy", "freeware", "hand", "stdok") for it in items):
        # Keine eigene Recherche: ehrlich als ungeprüft kennzeichnen, nicht als "Standard reicht".
        items.append({"status": "unrated"})

    def rank(it):
        st = it["status"]
        if st == "freeware" and it.get("addon"):
            st = "addon"
        return PRIORITY[st]

    items.sort(key=rank)
    return {"p": items[0]["status"], "items": items}


for ident, a in airports.items():
    a["sc"] = scenery_for(ident)
    text = content["airports"].get(ident, {})
    for k in ("hl", "brief", "tips", "tag", "level"):
        if k in text:
            a[k] = text[k]
    if ident in content.get("trials", {}):
        a["trial"] = content["trials"][ident]
    if ident in sim_checks:
        a["simCheck"] = sim_checks[ident]

# Ein Kandidat allein bewertet den Standard nicht: Der Airport braucht daneben ein Urteil (meist defaultOk).
unjudged = sorted(i for i, a in airports.items() if {"candidate", "unrated"} <= {it["status"] for it in a["sc"]["items"]})
if unjudged:
    sys.exit("Kandidat ohne Bewertung des Standards (defaultOk fehlt): " + ", ".join(unjudged))

# ---------- Legs in Flugreihenfolge ----------
by_anchor = defaultdict(list)
for e in route["excursions"]:
    by_anchor[e["anchor"]].append(e["id"])

legs = []
placed = set()
a320_n = 0
for ch in chapters:
    seq = ch["route"]
    for frm, to in zip(seq, seq[1:]):
        a320_n += 1
        nm = gc_nm(airports[frm], airports[to])
        air = a320_minutes(nm)
        leg = {"id": f"L{a320_n:03d}", "k": "a", "f": frm, "t": to, "ch": ch["id"], "n": a320_n,
               "nm": round(nm), "air": air, "blk": air + 20, "o2": air > 120}
        trials = content.get("trials", {})
        if to in trials or frm in trials:  # Landung und Start an der Sonderetappe testen
            leg["trial"] = to if to in trials else frm
        legs.append(leg)
        for xid in by_anchor.get(to, []):
            if xid in placed:
                continue
            placed.add(xid)
            e = excursions[xid]
            nm = gc_nm(airports[e["anchor"]], airports[e["target"]])
            for i, (a, b) in enumerate(((e["anchor"], e["target"]), (e["target"], e["anchor"])), 1):
                lid = f"X-{xid}-{i}"
                air = h160_minutes(nm)
                legs.append({"id": lid, "k": "h", "f": a, "t": b, "ch": ch["id"], "n": None,
                             "nm": round(nm), "air": air, "blk": None, "o2": air > 120, "x": xid})
                e["legs"].append(lid)
missing_x = set(excursions) - placed
if missing_x:
    sys.exit(f"Ausflüge ohne Anker in der Route: {sorted(missing_x)}")

visited = {airports[route["start"]]["cc"]}
first_leg = {airports[route["start"]]["cc"]: legs[0]["id"]}
cat_airports = defaultdict(list)
cat_via = {}
cat_airports[airports[route["start"]]["cc"]].append(route["start"])
cat_via[airports[route["start"]]["cc"]] = "a"
for leg in legs:
    cc = airports[leg["t"]]["cc"]
    if leg["t"] not in cat_airports[cc]:
        cat_airports[cc].append(leg["t"])
    if cc not in visited:
        visited.add(cc)
        leg["nc"] = [cc]
        first_leg[cc] = leg["id"]
        cat_via[cc] = leg["k"]

missing = sorted(set(CATEGORY_NAMES) - visited)
if missing:
    sys.exit("Nicht abgedeckte Volanta-Kategorien: " + ", ".join(f"{c} {CATEGORY_NAMES[c]}" for c in missing))

cats = [{"code": c, "name": CATEGORY_NAMES[c], "first": first_leg[c], "via": cat_via[c],
         "apts": cat_airports[c]} for c in sorted(CATEGORY_NAMES, key=lambda c: CATEGORY_NAMES[c])]

# ---------- Debriefing-Archiv prüfen (Regeln wie in V1) ----------
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ISO_TS = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2}(\.\d+)?)?(Z|[+-]\d{2}:\d{2})$")


def validate_debriefs(archive):
    errors = []
    if archive.get("schemaVersion") != 1:
        errors.append("schemaVersion muss 1 sein")
    entries = archive.get("entries")
    if not isinstance(entries, list):
        return {}, ["'entries' muss eine Liste sein"]
    by_id = {l["id"]: l for l in legs}
    seen = {}
    for n, e in enumerate(entries, 1):
        where = f"Eintrag {n} ({e.get('legId', '?')})"
        if not isinstance(e, dict):
            errors.append(f"{where}: kein Objekt")
            continue
        if any(isinstance(v, str) and v.startswith("<") and v.endswith(">") for v in e.values()):
            errors.append(f"{where}: Platzhalter aus der Vorlage nicht ersetzt")
        leg = by_id.get(e.get("legId"))
        if leg is None:
            errors.append(f"{where}: unbekannte Leg-ID")
        elif (e.get("from"), e.get("to")) != (leg["f"], leg["t"]):
            errors.append(f"{where}: Strecke {e.get('from')} → {e.get('to')} passt nicht zu {leg['f']} → {leg['t']}")
        if e.get("legId") in seen:
            errors.append(f"{where}: Leg-ID doppelt (schon Eintrag {seen[e['legId']]})")
        seen.setdefault(e.get("legId"), n)
        if e.get("status") not in ("draft", "final"):
            errors.append(f"{where}: status muss 'draft' oder 'final' sein")
        if not isinstance(e.get("updatedAt"), str) or not DATE.match(e["updatedAt"]):
            errors.append(f"{where}: updatedAt muss YYYY-MM-DD sein")
        if e.get("flightDate") is not None and (not isinstance(e["flightDate"], str) or not DATE.match(e["flightDate"])):
            errors.append(f"{where}: flightDate muss null oder YYYY-MM-DD sein")
        if e.get("volanta") not in ("open", "credited", "not_credited"):
            errors.append(f"{where}: volanta muss open, credited oder not_credited sein")
        if e.get("volantaAt") is not None and (not isinstance(e["volantaAt"], str) or not ISO_TS.match(e["volantaAt"])):
            errors.append(f"{where}: volantaAt muss ein ISO-Zeitstempel sein, z. B. 2026-09-24T18:30:00Z")
        if e.get("status") == "final":
            sc = e.get("actualScenery") or {}
            for side in ("departure", "arrival"):
                product = (sc.get(side) or {}).get("product")
                if not isinstance(product, str) or not product.strip():
                    errors.append(f"{where}: Finalbericht ohne tatsächlich genutzte Szenerie ({side})")
    return {e["legId"]: e for e in entries if isinstance(e, dict) and e.get("legId") in by_id}, errors


debrief_entries, debrief_errors = validate_debriefs(debriefs)
if debrief_errors:
    sys.exit("Debriefing-Archiv ungültig:\n  " + "\n  ".join(debrief_errors))

# ---------- Statistik ----------
a_legs = [l for l in legs if l["k"] == "a"]
h_legs = [l for l in legs if l["k"] == "h"]
owned_used = sorted({i for i in airports if i in OWNED})
main_route = {l["f"] for l in a_legs} | {l["t"] for l in a_legs}
v1_main = {l["from"] for l in v1["legs"]} | {l["to"] for l in v1["legs"]}
v1_used = {i["icao"] for i in v1["inventory"] if i["inRoute"]}
v1_bonus = {e["target"] for e in v1x["excursions"] if str(e.get("id", "")).startswith("BONUS")}
stats = {
    "a320": {"legs": len(a_legs), "nm": sum(l["nm"] for l in a_legs), "air": sum(l["air"] for l in a_legs)},
    "h160": {"legs": len(h_legs), "nm": sum(l["nm"] for l in h_legs), "air": sum(l["air"] for l in h_legs),
             "trips": len(excursions)},
    "legs": len(legs),
    "air": sum(l["air"] for l in legs),
    "over2h": sum(1 for l in legs if l["o2"]),
    "cats": len(visited),
    "ownedUsed": len(owned_used),
    "ownedMain": len([i for i in owned_used if i in main_route]),
    "ownedTotal": len(OWNED),
    "buy": sum(1 for a in airports.values() for it in a["sc"]["items"] if it["status"] == "buy"),
    # ungeprüft = kein Urteil über den Standard (auch wenn eine Payware-Option daneben steht)
    "unrated": sum(1 for a in airports.values() if any(it["status"] == "unrated" for it in a["sc"]["items"])),
    "scn": {st: sum(1 for a in airports.values() if a["sc"]["p"] == st)
            for st in ("owned", "buy", "freeware", "hand", "stdok", "optional", "unrated")},
    # kostenlose Kandidaten zum Prüfen (nie Hauptstatus) und offene Existenzprüfungen im Sim
    "candidate": sum(1 for a in airports.values() for it in a["sc"]["items"] if it["status"] == "candidate"),
    "simChecks": sorted(i for i, a in airports.items() if "simCheck" in a),
    "trials": sorted(content.get("trials", {})),
    "revisits": sorted({l["t"] for l in a_legs if sum(1 for m in a_legs if m["t"] == l["t"]) > 1}),
}
v1_legs = v1["legs"]
stats["v1"] = {
    "legs": len(v1_legs) + sum(len(e["legs"]) for e in v1x["excursions"]),
    "a320": len(v1_legs),
    "air": sum(l["airMin"] for l in v1_legs) + sum(l["airMin"] for e in v1x["excursions"] for l in e["legs"]),
    "over2h": sum(1 for l in v1_legs if l["over2h"]) + sum(1 for e in v1x["excursions"] for l in e["legs"] if l["over2h"]),
    "h160legs": sum(len(e["legs"]) for e in v1x["excursions"] if "Twin" not in e.get("aircraft", "")),
    "twinOtter": sum(len(e["legs"]) for e in v1x["excursions"] if "Twin" in e.get("aircraft", "")),
    "ownedUsed": len(v1_used | (v1_bonus & set(OWNED))),
    "ownedMain": len(v1_used & v1_main),
    "buy": 6,
    "default": 300,
}

chapter_out = []
for ch in chapters:
    ids = [l["id"] for l in legs if l["ch"] == ch["id"]]
    chapter_out.append({k: ch[k] for k in ("id", "title", "sub", "season")} | {"legs": ids, "route": ch["route"]})

today = datetime.date.today().isoformat()
data = {
    "meta": {"version": "V2", "built": today, "start": route["start"], "aircraft": route["aircraft"],
             "heli": route["helicopter"], "formula": route["timeFormula"]},
    "chapters": chapter_out,
    "airports": airports,
    "legs": legs,
    "excursions": excursions,
    "cats": cats,
    "changes": content["changes"],
    "research": content.get("research"),
    "stats": stats,
    "debriefs": debrief_entries,
    # Zuordnung der V1-Legs (für den Import einer V1-Fortschrittssicherung)
    "v1pairs": {str(l["id"]): f"{l['from']}>{l['to']}" for l in v1["legs"]}
               | {l["id"]: f"{l['from']}>{l['to']}" for e in v1x["excursions"] for l in e["legs"]},
    "owned": [{"icao": i, "name": r["Name"].strip(), "dev": r["Hersteller"].strip(), "store": r["Store"].strip(),
               "used": i in airports, "note": content["ownedNotes"].get(i)} for i, r in OWNED.items()],
}

with open(V2 / "tour-v2.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=1)

# ---------- HTML ----------
def script_json(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


template = (V2 / "template.html").read_text(encoding="utf-8")
css = (V2 / "app.css").read_text(encoding="utf-8")
app = (V2 / "app.js").read_text(encoding="utf-8")
world = (WORK / "world.json").read_text(encoding="utf-8").replace("</", "<\\/")
d3_inline = (WORK / "d3.min.js").read_text(encoding="utf-8")
topo_inline = (WORK / "topojson.min.js").read_text(encoding="utf-8")

def build_page(payload):
    return (template.replace("/*__CSS__*/", css)
            .replace("__TOUR_JSON__", script_json(payload))
            .replace("__WORLD_JSON__", world)
            .replace("/*__APP__*/", app))


# Lokal zeigt die Seite das Git-Archiv; im Artifact kommen Debriefings aus dessen Datenbank,
# damit ein Reset dort nichts Eingebettetes stehen lässt.
page = build_page(data | {"meta": data["meta"] | {"mode": "local"}})
artifact_page = build_page(data | {"meta": data["meta"] | {"mode": "artifact"}, "debriefs": {}})

local_libs = f"<script>{d3_inline}</script>\n<script>{topo_inline}</script>"
cdn_libs = ('<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js"></script>\n'
            '<script src="https://cdn.jsdelivr.net/npm/topojson-client@3.1.0/dist/topojson-client.min.js"></script>')

local = ('<!doctype html>\n<html lang="de">\n<head>\n<meta charset="utf-8">\n'
         '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
         + page.replace("<!--__LIBS__-->", local_libs) + "\n</html>\n")
(ROOT / "Volanta-Worldtour-V2.html").write_text(local, encoding="utf-8")

(V2 / "dist").mkdir(exist_ok=True)
(V2 / "dist" / "artifact.html").write_text(artifact_page.replace("<!--__LIBS__-->", cdn_libs), encoding="utf-8")

print(f"A320: {stats['a320']['legs']} Legs · {stats['a320']['nm']:,} NM · {stats['a320']['air'] / 60:.1f} h")
print(f"H160: {stats['h160']['trips']} Ausflüge · {stats['h160']['legs']} Legs · {stats['h160']['air'] / 60:.1f} h")
print(f"Gesamt: {stats['legs']} Legs · {stats['air'] / 60:.1f} h · über 2 h: {stats['over2h']}")
print(f"Kategorien: {stats['cats']}/245 · eigene Szenerien: Hauptroute {stats['ownedMain']}, "
      f"mit Ausflügen {stats['ownedUsed']}/{stats['ownedTotal']} (V1: {stats['v1']['ownedMain']} bzw. {stats['v1']['ownedUsed']})")
print("Szenerie-Status (Hauptstatus): " + " · ".join(f"{k} {v}" for k, v in stats["scn"].items()))
print(f"Szenerie ungeprüft: {stats['unrated']} Airports · Sonderetappen: {', '.join(stats['trials'])}")
print(f"Freeware zum Prüfen: {stats['candidate']} Kandidaten · offene Sim-Prüfungen: {', '.join(stats['simChecks']) or '–'}")
print(f"Debriefings im Archiv: {len(debrief_entries)} (geprüft)")
print(f"V1 zum Vergleich: {stats['v1']['legs']} Legs · {stats['v1']['air'] / 60:.1f} h · Twin Otter {stats['v1']['twinOtter']}")
print("Doppelt angeflogen:", ", ".join(stats["revisits"]) or "–")
print("Fertig:", ROOT / "Volanta-Worldtour-V2.html")
