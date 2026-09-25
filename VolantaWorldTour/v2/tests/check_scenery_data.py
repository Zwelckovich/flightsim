"""Prüft den Szenerie-Datenvertrag (candidate, dependencies, installNote, simChecks) und die Integration.

Aufruf:  python v2/tests/check_scenery_data.py
1. Der Build weist kaputte Szenerie-Daten ab (Testinhalte über WELTREISE_CONTENT, Abbruch vor jedem Schreiben).
2. Der normale Build reicht simChecks, Kandidaten und Abhängigkeiten an tour-v2.json durch (baut dabei neu).
3. integrate_research.py behält bei zwei Läufen mit den archivierten Rechercheergebnissen alle Angaben und
   ändert content.json nicht; wechselt ein Produktlink, bricht es ab, statt Angaben still zu verlieren.
   Gerechnet wird auf Kopien im Temp-Ordner – content.json und research-2026-09-24.json bleiben unberührt.
"""
import copy
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile

V2 = pathlib.Path(__file__).resolve().parent.parent
BUILD = V2 / "build_v2.py"
INTEGRATE = V2 / "integrate_research.py"
CONTENT = json.loads((V2 / "content.json").read_text(encoding="utf-8"))
ARCHIVE = json.loads((V2 / "research-2026-09-24.json").read_text(encoding="utf-8"))
SIM_CHECKS = ["FMZJ", "ZDM", "ZMCK", "ZZ-0002"]
CANDIDATES = {"LNMC", "NTTB", "VILH", "VRMM"}
# Ältere bezahlte Beobachtungskandidaten unter der Payware-Schwelle – so nennt sie SCOPE in integrate_research.py
PAID_WATCH = ["FACT", "FVFA", "MMMX", "NTAA", "OYSQ", "VILH", "VNKT", "VQPR"]
failures = []
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(errors="replace")


def run(script, *args, **env):
    return subprocess.run([sys.executable, "-B", str(script), *map(str, args)], capture_output=True, text=True,
                          encoding="utf-8", env=dict(os.environ, PYTHONIOENCODING="utf-8", **env))


def build_with(content):
    with tempfile.TemporaryDirectory() as tmp:
        path = pathlib.Path(tmp) / "content.json"
        path.write_text(json.dumps(content, ensure_ascii=False), encoding="utf-8")
        return run(BUILD, WELTREISE_CONTENT=str(path))


def expect_rejected(name, content, messages):
    res = build_with(content)
    if res.returncode == 0:
        failures.append(f"{name}: ungültige Daten wurden angenommen")
    for text in messages:
        if text not in res.stderr:
            failures.append(f"{name}: Fehler nicht erkannt: {text}")


def shown(rating):
    """Erste Bewertung aus Anzeigetexten wie „4,2 · 4“ oder „4,9 · 51 (Marketplace) · …“; ohne Bewertung 0."""
    m = re.match(r"\s*(\d),(\d+) · (\d+)", rating or "")
    return (float(f"{m[1]}.{m[2]}"), int(m[3])) if m else (0.0, 0)


# ---------- 1. Build weist kaputte Daten ab ----------
bad = copy.deepcopy(CONTENT)
sc = bad["scenery"]
sc["RJOO"]["dependencies"][0]["url"] = "flightsim.to/addon/111381"
sc["RJOO"]["dependencies"][1]["required"] = "ja"
sc["RJOO"]["dependencies"].append({"product": "X", "url": "https://example.org/x", "required": False, "link": "?"})
sc["VILH"]["required"] = True
sc["VRMM"]["installNote"] = " "
sc["YPKG"]["dependencies"] = []
sc["TEST__x"] = {"icao": "EDLV", "status": "gratis", "product": "X", "url": "https://example.org/x"}
bad["simChecks"]["ZMCK"]["status"] = "confirmed"
bad["simChecks"]["ZDM"]["sources"] = ["http://example.org/unsicher"]
bad["simChecks"]["ZZ-0002"]["note"] = ""
bad["simChecks"]["XXXX"] = {"status": "unconfirmed", "note": "x", "sources": ["https://example.org/x"]}
expect_rejected("Vertrag", bad, [
    "Szenerie RJOO: Abhängigkeit 1 braucht Produkt und https-Link",
    "Szenerie RJOO: Abhängigkeit 2: required muss true oder false sein",
    "Szenerie RJOO: Abhängigkeit 3 hat unbekannte Felder ['link']",
    "Szenerie VILH: ein Kandidat kann keine Pflicht sein",
    "Szenerie VRMM: installNote ist leer",
    "Szenerie YPKG: dependencies muss eine nicht leere Liste sein",
    "Szenerie TEST__x: unbekannter Status 'gratis'",
    "simChecks ZMCK: status muss 'unconfirmed' sein",
    "simChecks ZDM: sources braucht mindestens einen https-Link",
    "simChecks ZZ-0002: note fehlt",
    "simChecks XXXX: Landeplatz nicht in der Tour",
])
lonely = copy.deepcopy(CONTENT)
del lonely["defaultOk"]["VRMM"]
expect_rejected("Kandidat ohne Urteil", lonely, ["Kandidat ohne Bewertung des Standards (defaultOk fehlt): VRMM"])

# ---------- 2. Normaler Build reicht alles durch ----------
normal = run(BUILD)
if normal.returncode != 0:
    failures.append("normaler Build fehlgeschlagen:\n" + normal.stderr)
else:
    tour = json.loads((V2 / "tour-v2.json").read_text(encoding="utf-8"))
    ap = tour["airports"]
    checks = sorted(i for i, a in ap.items() if a.get("simCheck"))
    if checks != SIM_CHECKS or tour["stats"]["simChecks"] != SIM_CHECKS:
        failures.append(f"simCheck durchgereicht an {checks}, erwartet {SIM_CHECKS}")
    if any(ap[i]["simCheck"]["status"] != "unconfirmed" for i in checks):
        failures.append("simCheck mit anderem Status als 'unconfirmed'")
    cands = {i for i, a in ap.items() if any(it["status"] == "candidate" for it in a["sc"]["items"])}
    if cands != CANDIDATES or tour["stats"]["candidate"] != len(CANDIDATES):
        failures.append(f"Kandidaten: {sorted(cands)}, erwartet {sorted(CANDIDATES)}")
    for i in sorted(cands):
        sts = [it["status"] for it in ap[i]["sc"]["items"]]
        if ap[i]["sc"]["p"] == "candidate" or "unrated" in sts or not {"stdok", "hand"} & set(sts):
            failures.append(f"{i}: Kandidat ohne Urteil über den Standard ({sts})")
        if "freeware" in sts:
            failures.append(f"{i}: Kandidat steht zusätzlich als Freeware-Empfehlung da")
    rjoo = next((it for it in ap["RJOO"]["sc"]["items"] if it["status"] == "freeware"), {})
    if "alt" in rjoo or not any(d["required"] and "/111381/" in d["url"] for d in rjoo.get("dependencies", [])):
        failures.append("RJOO: WU20-Fix nicht als Pflicht-Abhängigkeit (statt Alternative) durchgereicht")
    for i, part in (("RJOO", "/34494/"), ("DNMM", "/6199/"), ("VOCI", "/34494/"), ("ELLX", "/12973/"), ("YPKG", "/1886/")):
        deps = [d for it in ap[i]["sc"]["items"] for d in it.get("dependencies", []) if d["required"]]
        if not any(part in d["url"] for d in deps):
            failures.append(f"{i}: Pflicht-Abhängigkeit {part} fehlt")
    rules = tour["research"]["rules"]
    for banned in ("Standard geprüft", "für alle Airports", "nach denselben Regeln"):
        if banned in rules:
            failures.append(f"Regeltext enthält noch: {banned}")
    for i, a in ap.items():
        if any(it["status"] == "stdok" and "Standard reicht" in (it.get("why") or "") for it in a["sc"]["items"]):
            failures.append(f"{i}: Begründung behauptet weiter, der Standard reiche")

# Reichweite der Ausnahmen: jeder bezahlte Beobachtungskandidat unter der Schwelle steht im Regeltext
watch = sorted(s.get("icao", k) for k, s in CONTENT["scenery"].items()
               if s["status"] == "optional" and not k.endswith("__pw")
               and not (shown(s.get("rating"))[0] >= 4.3 and shown(s.get("rating"))[1] >= 10))
if watch != PAID_WATCH:
    failures.append(f"bezahlte Beobachtungskandidaten {watch} passen nicht zur Liste in SCOPE {PAID_WATCH}")
for i in watch:
    if i not in CONTENT["research"]["rules"]:
        failures.append(f"Regeltext nennt den bezahlten Beobachtungskandidaten {i} nicht")
# Ältere Freeware-Empfehlungen außerhalb des Rechercheaufs erfüllen die Zahlen-Schwelle (4,5 bei ≥ 8 Bewertungen)
for k, s in CONTENT["scenery"].items():
    if s["status"] == "freeware" and not k.endswith("__fw"):
        r, n = shown(s.get("rating"))
        if r < 4.5 or n < 8:
            failures.append(f"{k}: ältere Freeware-Empfehlung unter der Schwelle ({s.get('rating')})")

# ---------- 3. Integration behält alles und ist wiederholbar ----------
with tempfile.TemporaryDirectory() as tmp:
    tmp = pathlib.Path(tmp)
    src = tmp / "recherche"
    src.mkdir()
    results = list(ARCHIVE["results"].values())
    (src / "B001.json").write_text(json.dumps([{"icao": r["icao"]} for r in results], ensure_ascii=False), encoding="utf-8")
    (src / "B001-result.json").write_text(json.dumps(results, ensure_ascii=False), encoding="utf-8")
    work = tmp / "content.json"
    work.write_text(json.dumps(CONTENT, ensure_ascii=False, indent=1), encoding="utf-8")
    env = {"WELTREISE_CONTENT": str(work), "WELTREISE_RESEARCH_OUT": str(tmp / "research.json")}

    first = run(INTEGRATE, src, **env)
    if first.returncode != 0:
        failures.append("Integration (1. Lauf) abgebrochen:\n" + first.stdout + first.stderr)
    else:
        once = json.loads(work.read_text(encoding="utf-8"))
        archive = json.loads((tmp / "research.json").read_text(encoding="utf-8"))
        changed = sorted(i for i, v in ARCHIVE["decisions"].items() if archive["decisions"].get(i) != v)
        if changed:
            failures.append(f"Integration ändert Entscheidungen: {changed}")
        for key, s in CONTENT["scenery"].items():
            for field in ("status", "dependencies", "installNote"):
                if field in s and once["scenery"].get(key, {}).get(field) != s[field]:
                    failures.append(f"Integration verliert oder ändert {key}.{field}")
        if once.get("simChecks") != CONTENT.get("simChecks"):
            failures.append("Integration verändert simChecks")
        diff = [f"{sec}.{k}" for sec, part in CONTENT.items() if isinstance(part, dict)
                for k in set(part) | set(once.get(sec, {})) if part.get(k) != once.get(sec, {}).get(k)]
        diff += [sec for sec, part in CONTENT.items() if not isinstance(part, dict) and part != once.get(sec)]
        if diff:
            failures.append("Integration weicht von content.json ab: " + ", ".join(sorted(diff)[:20]))

        second = run(INTEGRATE, src, **env)
        if second.returncode != 0:
            failures.append("Integration (2. Lauf) abgebrochen:\n" + second.stdout + second.stderr)
        elif json.loads(work.read_text(encoding="utf-8")) != once:
            failures.append("zweiter Integrationslauf verändert das Ergebnis")
        if "bleibt unverändert" not in second.stdout:
            failures.append("Archivschutz greift nicht: der zweite Lauf hätte das Archiv überschrieben")

    moved = copy.deepcopy(CONTENT)
    moved["scenery"]["ELLX__fw"]["url"] = "https://flightsim.to/addon/1/anderes-produkt"
    work.write_text(json.dumps(moved, ensure_ascii=False, indent=1), encoding="utf-8")
    third = run(INTEGRATE, src, **env)
    if third.returncode == 0 or "ELLX__fw" not in third.stdout:
        failures.append("Integration verwirft Installationsangaben still, wenn der Produktlink wechselt")

if failures:
    print("FAIL\n  " + "\n  ".join(failures))
    sys.exit(1)
print(f"PASS · Vertrag geprüft ({len(SIM_CHECKS)} Sim-Prüfungen, {len(CANDIDATES)} Kandidaten), "
      "Integration zweimal ohne Verlust, Build neu erstellt")
