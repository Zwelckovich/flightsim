"""Prüft, dass der Build fehlerhafte Debriefing-Archive abweist und gültige annimmt.

Aufruf:  python v2/tests/check_debriefs.py
Der Build läuft dabei mit Testarchiven; am Ende wird normal neu gebaut.
"""
import json
import os
import pathlib
import subprocess
import sys
import tempfile

V2 = pathlib.Path(__file__).resolve().parent.parent
BUILD = V2 / "build_v2.py"

BAD = {
    "schemaVersion": 1, "tour": "EDLV-V2",
    "entries": [
        {"legId": "L001", "from": "EDLV", "to": "EBBR", "status": "done", "updatedAt": "2026-09-24", "flightDate": None, "volanta": "open"},
        {"legId": "L002", "from": "EHAM", "to": "EBBR", "status": "final", "updatedAt": "2026-09-24", "flightDate": "24.09.2026",
         "volanta": "credited", "actualScenery": {"departure": {"product": "FlyTampa EHAM"}, "arrival": {"product": None}}},
        {"legId": "L002", "from": "EHAM", "to": "EBBR", "status": "draft", "updatedAt": "2026-09-24", "flightDate": None,
         "volanta": "maybe", "volantaAt": "heute"},
        {"legId": "<feste Leg-ID>", "from": "<ICAO Abflug>", "to": "<ICAO Ankunft>", "status": "draft", "updatedAt": "YYYY-MM-DD",
         "flightDate": None, "volanta": "open"},
    ],
}
EXPECTED = [
    "Strecke EDLV → EBBR passt nicht",
    "status muss 'draft' oder 'final' sein",
    "flightDate muss null oder YYYY-MM-DD sein",
    "Finalbericht ohne tatsächlich genutzte Szenerie (arrival)",
    "Leg-ID doppelt",
    "volanta muss open, credited oder not_credited sein",
    "volantaAt muss ein ISO-Zeitstempel sein",
    "Platzhalter aus der Vorlage nicht ersetzt",
    "unbekannte Leg-ID",
    "updatedAt muss YYYY-MM-DD sein",
]
GOOD = {
    "schemaVersion": 1, "tour": "EDLV-V2",
    "entries": [
        {"legId": "L001", "from": "EDLV", "to": "EHAM", "status": "final", "updatedAt": "2026-09-24", "flightDate": "2026-09-24",
         "aircraft": "Fenix A320", "volanta": "credited", "volantaAt": "2026-09-24T18:30:00Z",
         "actualScenery": {"departure": {"product": "SimPixel EDLV", "version": None}, "arrival": {"product": "FlyTampa EHAM", "version": None}, "landscape": "keine"}},
    ],
}


def run(archive):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(archive, f, ensure_ascii=False)
        path = f.name
    env = dict(os.environ, WELTREISE_DEBRIEFS=path, PYTHONIOENCODING="utf-8")
    try:
        return subprocess.run([sys.executable, "-B", str(BUILD)], capture_output=True, text=True, encoding="utf-8", env=env)
    finally:
        os.unlink(path)


failures = []
bad = run(BAD)
if bad.returncode == 0:
    failures.append("fehlerhaftes Archiv wurde angenommen")
for text in EXPECTED:
    if text not in bad.stderr:
        failures.append(f"Fehler nicht erkannt: {text}")
good = run(GOOD)
if good.returncode != 0:
    failures.append("gültiges Archiv wurde abgewiesen:\n" + good.stderr)

# Normalen Stand wiederherstellen
subprocess.run([sys.executable, "-B", str(BUILD)], capture_output=True, text=True, encoding="utf-8",
               env=dict(os.environ, PYTHONIOENCODING="utf-8"), check=True)

if failures:
    print("FAIL\n  " + "\n  ".join(failures))
    sys.exit(1)
print(f"PASS · {len(EXPECTED)} Fehlerfälle abgewiesen, gültiges Archiv angenommen, Build wiederhergestellt")
