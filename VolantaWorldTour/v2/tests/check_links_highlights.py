"""Data regressions for product references and highlight coverage; uses temporary inputs."""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

v2 = Path(__file__).resolve().parent.parent
load = lambda name: json.loads((v2 / name).read_text(encoding="utf-8"))
data = load("tour-v2.json")
links = load("scenery-links.json")
audit = load("highlight-audit.json")
content = load("content.json")

assert len(data["legs"]) == 423 and len(data["cats"]) == 245
assert data["legs"][0]["f"] == data["legs"][-1]["t"] == "EDLV"
for a, b in zip(data["legs"], data["legs"][1:]):
    assert a["t"] == b["f"], (a["id"], b["id"])
for ident, refs in links.items():
    assert data["airports"][ident]["sceneryLinks"] == refs
    assert len({r["url"] for r in refs}) == len(refs), ident
for entry in data["highlightAudit"]["airports"]:
    assert entry["legs"] == [l["id"] for l in data["legs"] if l["t"] == entry["icao"]]
assert "VHHX" not in data["airports"]
assert data["airports"]["UKLL"]["operatingNote"]["url"].startswith("https://www.easa.europa.eu/")
assert data["airports"]["TFFJ"]["level"] == 2
assert data["airports"]["KSFO"]["level"] == content["airports"]["KSFO"]["level"]

def rejected(value, env_key, expected):
    with tempfile.TemporaryDirectory() as tmp:
        file = Path(tmp) / "input.json"
        file.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
        p = subprocess.run([sys.executable, "-X", "utf8", str(v2 / "build_v2.py")],
            env={**os.environ, env_key: str(file)}, capture_output=True, text=True, encoding="utf-8")
        assert p.returncode != 0 and expected in p.stderr, (p.stdout, p.stderr)

bad = copy.deepcopy(links)
bad["EDLV"] = [{"label":"Bad", "context":"Bad", "url":"javascript:alert(1)"}]
rejected(bad, "WELTREISE_SCENERY_LINKS", "https-Link nötig")
bad = copy.deepcopy(content)
bad["scenery"][next(iter(bad["scenery"]))]["alt"] = {"name":"Missing link"}
rejected(bad, "WELTREISE_CONTENT", "Alternative braucht Name und https-Link")
bad = copy.deepcopy(audit)
bad["airports"][0]["icao"] = "VHHX"
rejected(bad, "WELTREISE_HIGHLIGHT_AUDIT", "kein aktiver Airport-Datensatz")
bad = copy.deepcopy(audit)
next(e for e in bad["airports"] if e["icao"] == "TNCS")["activeSources"] = []
rejected(bad, "WELTREISE_HIGHLIGHT_AUDIT", "fehlender Betriebsnachweis")
identities = load("leg-identities.json")
active = {l["id"]: l for l in data["legs"] if l["k"] == "a"}
assert "L106" not in active and identities["L106"]["retired"]
for lid, identity in identities.items():
    if identity.get("retired"):
        assert lid not in active
    else:
        assert {k: active[lid][k] for k in ("f", "t", "ch")} == identity
assert (active["L389"]["f"], active["L389"]["t"]) == ("KPHX", "KSAN")
assert (active["L390"]["f"], active["L390"]["t"]) == ("KSAN", "KLAS")
assert active["L389"]["air"] <= 120 and active["L390"]["air"] <= 120
assert sum(not a["legs"] for a in data["highlightAudit"]["airports"]) == 11
print("PASS links/highlights: connected route with stable identities, all references preserved, actual-arrival coverage, closed airport and unsafe/missing URLs rejected")
