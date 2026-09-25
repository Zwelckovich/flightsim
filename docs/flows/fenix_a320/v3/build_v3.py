"""Baut Fenix_A320_Flow_V3.html aus flow-v3.json, template.html, app.css und app.js.

Aufruf:  python v3/build_v3.py
Die Ausgabe ist eine einzelne, offline nutzbare HTML-Datei (Schriften kommen optional von Google Fonts,
ohne Internet greifen Arial Narrow und Consolas). Vor dem Schreiben wird die Datenquelle streng geprüft;
bei Fehlern bricht der Build ab und nennt jede Fundstelle.
"""
import json
import pathlib
import re
import sys

V3 = pathlib.Path(__file__).resolve().parent
OUT = V3.parent / "Fenix_A320_Flow_V3.html"
data = json.loads((V3 / "flow-v3.json").read_text(encoding="utf-8"))

TYPES = {"act", "chk", "tgt", "cau", "wrn"}
KINDS = {"flow", "special", "checklist", "reference"}
PLATES = {"zones", "takeoff", "approach", "eo", "goaround", "gsabove", "circling", "visual", "quickreturn"}
FORBIDDEN = re.compile(r"Eurowings|\bEW\b|V2500|\bIAE\b|V1 cited|V2 is prepared|legacy FSLabs", re.I)
errors = []


def err(where, msg):
    errors.append(f"{where}: {msg}")


fields = {f["id"]: f for f in data["fields"]}
profile = {p["id"]: {o[0] for o in p["options"]} for p in data["profile"]}
for p in data["profile"]:
    if p["default"] not in profile[p["id"]]:
        err(f"profile.{p['id']}", "Standardwert ist keine Option")
placeholders = set(fields) | set(profile)
sources = set(data["sources"])
phases = {p["id"]: p for p in data["phases"]}
if len(phases) != len(data["phases"]):
    err("phases", "doppelte Bereichs-ID")


def check_when(where, when):
    for k, v in (when or {}).items():
        if k not in profile:
            err(where, f"unbekannte Profilbedingung {k!r}")
            continue
        for x in (v if isinstance(v, list) else [v]):
            if x not in profile[k]:
                err(where, f"Profilwert {x!r} gibt es für {k} nicht")


def check_text(where, s):
    if not isinstance(s, str):
        return
    for m in re.findall(r"\{\{(\w+)\}\}", s):
        if m not in placeholders:
            err(where, f"unbekannter Platzhalter {{{{{m}}}}}")
    if re.search(r"<[a-z/]", s):
        err(where, "HTML im Text – nur **fett** ist erlaubt")
    if s.count("**") % 2:
        err(where, "unpaarige ** im Text")
    if FORBIDDEN.search(s):
        err(where, f"Altlast im Text: {FORBIDDEN.search(s).group(0)!r}")


ids = set()
for p in data["phases"]:
    pid = p["id"]
    if p.get("kind") not in KINDS:
        err(pid, f"unbekannte Art {p.get('kind')!r}")
    for k in ("title", "note"):
        check_text(f"{pid}.{k}", p.get(k))
    for f in p.get("fields", []):
        if f not in placeholders:
            err(pid, f"unbekanntes Datenfeld {f!r}")
    for c in p.get("checklists", []):
        if phases.get(c, {}).get("kind") != "checklist":
            err(pid, f"verlinkte Checkliste {c!r} fehlt")
    if p.get("plate") and p["plate"] not in PLATES:
        err(pid, f"unbekanntes Profil {p['plate']!r}")
    for n, it in enumerate(p["items"]):
        where = f"{pid}[{n}]"
        if "sub" in it:
            check_text(where, it["sub"])
            continue
        if "line" in it or "table" in it:
            if "table" in it:
                for row in it["table"]["rows"]:
                    for cell in row:
                        check_text(where, cell)
            continue
        iid = it.get("id")
        if not iid:
            err(where, "Schritt ohne ID")
            continue
        where = f"{pid}/{iid}"
        if iid in ids:
            err(where, "doppelte Schritt-ID")
        ids.add(iid)
        for k in ("item", "state"):
            if not it.get(k):
                err(where, f"{k} fehlt")
        if it.get("type") not in TYPES:
            err(where, f"unbekannter Typ {it.get('type')!r}")
        if it.get("src") not in sources:
            err(where, f"unbekannte Quelle {it.get('src')!r}")
        for k in ("item", "state", "caution", "detail"):
            check_text(f"{where}.{k}", it.get(k))
        check_when(where, it.get("when"))
        if it.get("link") and phases.get(it["link"], {}).get("kind") != "checklist":
            err(where, f"Link auf {it['link']!r} ist keine Checkliste")
for f in data["fields"]:
    check_when(f"field.{f['id']}", f.get("when"))

flow = [p["id"] for p in data["phases"] if p["kind"] == "flow"]
staged = [pid for s in data["stages"] for pid in s["phases"]]
if sorted(staged) != sorted(flow) or len(staged) != len(set(staged)):
    err("stages", "Abschnitte decken den Normal Flow nicht genau einmal ab")
for s in data["stages"]:
    if [pid for pid in flow if pid in s["phases"]] != s["phases"]:
        err(f"stage.{s['id']}", "Reihenfolge weicht vom Normal Flow ab")

if errors:
    sys.exit("flow-v3.json ungültig:\n  " + "\n  ".join(errors))

template = (V3 / "template.html").read_text(encoding="utf-8")
css = (V3 / "app.css").read_text(encoding="utf-8")
app = (V3 / "app.js").read_text(encoding="utf-8")
payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
for marker in ("/*__CSS__*/", "__FLOW_JSON__", "/*__APP__*/"):
    if template.count(marker) != 1:
        sys.exit(f"Platzhalter {marker} fehlt im Template oder kommt mehrfach vor")
page = template.replace("/*__CSS__*/", css).replace("__FLOW_JSON__", payload).replace("/*__APP__*/", app)
OUT.write_text(page, encoding="utf-8")

kinds = {k: sum(1 for p in data["phases"] if p["kind"] == k) for k in ("flow", "special", "checklist", "reference")}
print(f"geprüft: {len(ids)} Schritte · {kinds['flow']} Phasen · {kinds['special']} Sonderverfahren · "
      f"{kinds['checklist']} Checklisten · {kinds['reference']} Referenzseiten")
print(f"geschrieben: {OUT.name} · {OUT.stat().st_size / 1024:.0f} KB")
