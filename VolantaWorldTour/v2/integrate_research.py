"""Übernimmt die Szenerie-Recherche (B*-result.json) nach festen Schwellen in content.json.

Aufruf:  python v2/integrate_research.py <Ordner mit B*.json und B*-result.json> [--dry] [--replace-archive]

Schwellen für die Airports dieses Laufs (Zahlen: Recherche vom 24.09.2026):
- Freeware-Empfehlung: Bewertung ≥ 4,5, mindestens 8 Bewertungen oder 6.000 Downloads, MSFS 2024 belegt
  (Tag auf flightsim.to oder Aussage von Autor bzw. Nutzern). Getrennte 2020-/2024-Einträge derselben
  Szenerie und Basis + Pflicht-Erweiterung zählen zusammen (COMBINED, Zahlen nachgeprüft).
- Payware als Option: Bewertung ≥ 4,3, mindestens 10 Bewertungen, für MSFS 2024 gelistet oder belegt.
- Sonst Kennung stdok („Angebot recherchiert“) mit der Begründung aus der Recherche: Es fand sich kein Add-on
  mit belegtem Mehrwert. Die Standardszenerie selbst ist damit nicht im Simulator geprüft.
- Kostenlose Kandidaten unter der Schwelle kommen nur mit eigener Begründung (CANDIDATE) als Status candidate
  neben das stdok-Urteil – als „Freeware zum Prüfen“, nie als Empfehlung.
Ein Qualitätsbefund (veraltetes Layout, bekannte Fehler in 2024) kann eine Empfehlung trotz Schwelle
verhindern (QUALITY_BLOCK), aber nie eine unter der Schwelle erzeugen. Jede Abweichung vom Urteil der
Recherche wird ausgegeben. Airports mit Urteil „unverified“ bleiben ehrlich „ungeprüft“.

Nicht angefasst werden die von Hand gepflegten Teile: Kauf-Tipps, ältere Einträge ohne __fw/__pw/__cand im
Schlüssel, simChecks und alle Texte außer defaultOk der Airports dieses Laufs. Welche davon außerhalb der
Schwellen liegen, nennt SCOPE ausdrücklich.
Beim erneuten Lauf bleiben dependencies und installNote an erzeugten Einträgen erhalten, solange der
Produktlink gleich bleibt. Passt ein Eintrag nicht mehr, bricht das Skript ab, statt die Angaben zu verlieren.
Das Archiv research-<Datum>.json wird nur neu geschrieben, wenn es fehlt oder --replace-archive gesetzt ist,
damit die damaligen Belege erhalten bleiben. Tests leiten die Pfade über WELTREISE_CONTENT und
WELTREISE_RESEARCH_OUT um (siehe tests/check_scenery_data.py).
"""
import json
import os
import pathlib
import re
import sys
import unicodedata

V2 = pathlib.Path(__file__).resolve().parent
SRC = pathlib.Path(sys.argv[1])
DRY = "--dry" in sys.argv
REPLACE_ARCHIVE = "--replace-archive" in sys.argv
DATE = "2026-09-24"
content_path = pathlib.Path(os.environ.get("WELTREISE_CONTENT", V2 / "content.json"))
archive_path = pathlib.Path(os.environ.get("WELTREISE_RESEARCH_OUT", V2 / f"research-{DATE}.json"))
content = json.loads(content_path.read_text(encoding="utf-8"))

FW_RATING, FW_COUNT, FW_DOWNLOADS = 4.5, 8, 6000
PW_RATING, PW_COUNT = 4.3, 10
RULES = ("Freeware-Empfehlung ab 4,5 Sternen bei mindestens 8 Bewertungen oder 6.000 Downloads und belegtem "
         "MSFS-2024-Betrieb (Tag, Autor oder Nutzer). Payware-Option ab 4,3 Sternen bei mindestens 10 Bewertungen "
         "und MSFS-2024-Angabe. Kostenlose Kandidaten unter der Schwelle stehen nur als „Freeware zum Prüfen“ da. "
         "Ohne belegten Mehrwert: „Angebot recherchiert“ mit Begründung. Preise: günstigster Händler laut "
         "FSAddonCompare, meist ohne Steuern.")
# Reichweite der Schwellen: Was außerhalb liegt, steht hier mit Namen (tests/check_scenery_data.py gleicht die
# Liste der bezahlten Beobachtungskandidaten mit content.json ab).
SCOPE = ("Die Schwellen gelten für die {airports} Airports dieser Recherche und für die älteren Freeware-Einträge "
         "(am 24.09.2026 nachgezählt; VILH, VRMM und NTTB stehen seitdem nur noch zum Prüfen da). Ausgenommen, "
         "jeweils mit eigener Begründung: die handverlesenen Kauf-Tipps und ältere bezahlte Beobachtungskandidaten "
         "unter der Payware-Schwelle (FACT, VNKT, OYSQ, FVFA/FSDG, VQPR/FSDG, NTAA, MMMX, VILH/Sundownersim) – "
         "diese bleiben optional.")

# Dieselbe Szenerie mit getrennten Einträgen: niedrigere Bewertung, Summe der Bewertungen und Downloads.
COMBINED = {
    "TFFF": (5.0, 19, 5898, "5,0 · 6 (+ 13 der 2020-Fassung)"),
    "FYWH": (5.0, 28, 11145, "5,0 · 3 (+ 25 der 2020-Fassung)"),
    "PKMJ": (4.9, 17, 4671, "5,0 · 5 (+ 4,9 · 12 der 2020-Fassung)"),
    "PGUM": (4.9, 11, 10355, "5,0 · 3 (+ 4,9 · 8 der 2020-Fassung)"),
    "YPCC": (5.0, 12, 3915, "5,0 · 2 (+ 10 der 2020-Fassung)"),
    "DNMM": (4.6, 23, 10836, "5,0 · 3 · Basis-Szenerie 4,6 · 20"),
}
# Freeware erfüllt die Schwelle, die Recherche rät wegen eines Qualitätsbefunds trotzdem ab.
QUALITY_BLOCK = {
    "SVMI": "Freeware von 2021 kollidiert laut Nutzern mit dem geänderten Standard-Terminal.",
    "VTBS": "Freeware von 2020 mit altem Bahnlayout und fehlenden Anflügen.",
    "NTAA": "Zwei MSFS-2024-Nutzer melden fehlende Bahn- und Bodenmarkierungen; der Autor pflegt die Szenerie nicht mehr.",
}
# Dieselbe Payware mit zwei Listungen: beide Bewertungen zeigen statt nur der besseren.
RATING_SHOWN = {"WADD": "4,9 · 51 (Marketplace) · 4,2 · 20 (Aerosoft)"}
# Eigene Begründung, wo das Ergebnis vom Urteil der Recherche abweicht oder deren Text präzisiert wurde
# (EGYP, HAAB: MSFS 2024 nur durch Nutzer belegt, nicht vom Autor).
REASON = {
    "NFFN": "iniBuilds Nadi (4,34 aus 56, für MSFS 2020/2024) ist die beste Aufwertung, aber kein Muss. "
            "Die Mountainair-Freeware V5 (4,4 aus 11) liegt knapp unter der Freeware-Schwelle von 4,5.",
    "LNMC": "Die CDN-Freeware für MSFS 2024 (5,0 aus 7, 1.172 Downloads, v1.1 vom April 2026) liegt unter der "
            "Schwelle von 8 Bewertungen und steht deshalb nur als Kandidat zum Prüfen daneben. Die ältere "
            "2020-Fassung von t0kenkiwi hat 4,3 aus 26.",
    "LTCG": "Freeware von armortas (5,0 aus 7, 8.378 Downloads), im Juni 2026 an MSFS 2024 angepasst.",
    "EGYP": "Freeware von Flak, 5,0 aus 11 Bewertungen, 7.693 Downloads. Dass sie in MSFS 2024 läuft, beruht auf "
            "einem Nutzerbericht, den der Autor begrüßt; getestet hat er v1.9.1 laut Changelog aber nur in MSFS "
            "2020 (natives 2024-Update noch geplant).",
    "HAAB": "Freeware von Viktoren69 mit 4,9 aus 22 Bewertungen und 13.110 Downloads, nur als MSFS 2020 getaggt, "
            "laut Nutzerberichten (2025/2026) aber in MSFS 2024 nutzbar (gemeldeter Taxiway-Versatz, sechs "
            "kosmetische Zusatzbibliotheken), während die 2024-Paywares kaum bewertet sind (African Skies 5,0 aus 2, Barelli 4,0 "
            "aus 3). Der Autor nennt nur MSFS 2020: Die Szenerie sei für 2020 gedacht und in 2024 nie getestet; auf "
            "Nachfrage schreibt er, sie laufe nur in 2020. Dass sie in MSFS 2024 läuft, ist damit nicht vom Autor "
            "bestätigt – die Nutzerberichte widersprechen seiner Aussage.",
}
# Kostenlose Kandidaten: unter der Freeware-Schwelle, deshalb keine Empfehlung – aber mit belegter 2024-Fassung
# einen Test wert. Nur mit Urteil stdok oder optional; das defaultOk des Airports bleibt stehen.
CANDIDATE = {
    "LNMC": "Kostenloser Kandidat, keine Empfehlung: 5,0 aus erst 7 Bewertungen bei 1.172 Downloads – unter der "
            "Freeware-Schwelle. Eigene MSFS-2024-Fassung (v1.1 vom 19.04.2026), gebaut für ein IVAO-Event zum Grand "
            "Prix; eine Nutzermeldung über ausgehende Triebwerke beim Spawnen weist der Autor zurück, die Szene "
            "wirke nicht auf Luftfahrzeuge ein.",
}
HAND_LABEL = {"SEQM": "Basis-Sim"}
VERDICTS = {"freeware", "optional", "buy", "handcrafted", "stdok", "unverified"}


def de(x):
    if not isinstance(x, (int, float)):
        return None
    return (f"{x:.1f}" if round(x * 10) == x * 10 else f"{x:.2f}").replace(".", ",")


def thousands(n):
    return f"{n:,}".replace(",", ".")


def num(x):
    return x if isinstance(x, (int, float)) else 0


def fw_numbers(icao, fw):
    if icao in COMBINED:
        r, n, dl, _ = COMBINED[icao]
        return r, n, dl
    return num(fw.get("rating")), num(fw.get("count")), num(fw.get("downloads"))


def fw_ok(icao, fw):
    if not fw or fw.get("msfs2024") != "ja":
        return False
    r, n, dl = fw_numbers(icao, fw)
    return r >= FW_RATING and (n >= FW_COUNT or dl >= FW_DOWNLOADS)


def pw_ok(pw):
    return bool(pw) and pw.get("msfs2024") == "ja" and num(pw.get("rating")) >= PW_RATING and num(pw.get("count")) >= PW_COUNT


def fw_rating(icao, fw):
    if icao in COMBINED:
        return COMBINED[icao][3]
    parts = [f"{de(fw['rating'])} · {fw.get('count') or 0}"] if isinstance(fw.get("rating"), (int, float)) else []
    if fw.get("downloads"):
        parts.append(f"{thousands(fw['downloads'])} Downloads")
    return " · ".join(parts) or None


def fw_desc(icao, fw):
    r, n, dl = fw_numbers(icao, fw)
    s = f"Freeware {de(r)} · {n}" + (f" · {thousands(dl)} Downloads" if dl else "")
    return s + ("" if fw.get("msfs2024") == "ja" else f", MSFS 2024 {fw.get('msfs2024') or 'unklar'}")


def pw_desc(pw):
    s = f"Payware {pw.get('dev')} {de(pw.get('rating'))} · {pw.get('count')}"
    return s + ("" if pw.get("msfs2024") == "ja" else f", MSFS 2024 {pw.get('msfs2024') or 'unklar'}")


def pw_rating(pw):
    return f"{de(pw['rating'])} · {pw.get('count') or 0}" if isinstance(pw.get("rating"), (int, float)) else None


def short_price(p):
    if not p:
        return None
    m = re.search(r"(ab\s+)?\d{1,3}(?:,\d{2})?\s?(?:€|\$|£)", p)
    return m.group(0) if m else p[:40]


def sentence(s):
    s = s.strip()
    return s if s.endswith((".", "!", "?")) else s + "."


def neutral(text):
    """„Angebot recherchiert“ ist kein Test der Standardszenerie – also auch keine Aussage, dass sie reicht."""
    return text.replace("– der Standard reicht", "– kein Add-on mit belegtem Mehrwert")


def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]", "", s)


def same_dev(a, b):
    a, b = norm(a), norm(b)
    return bool(a and b) and (a in b or b in a)


# ---------- Ergebnisse einlesen und formal prüfen ----------
results, problems = {}, []
for f in sorted(SRC.glob("B*-result.json")):
    batch = json.loads(f.read_text(encoding="utf-8"))
    expected = [x["icao"] for x in json.loads((SRC / f.name.replace("-result", "")).read_text(encoding="utf-8"))]
    got = [r.get("icao") for r in batch]
    if sorted(got) != sorted(expected):
        problems.append(f"{f.name}: Airports passen nicht zur Eingabe (fehlend {sorted(set(expected) - set(got))}, zusätzlich {sorted(set(got) - set(expected))})")
    for r in batch:
        i = r.get("icao")
        if r.get("verdict") not in VERDICTS:
            problems.append(f"{i}: unbekanntes Urteil {r.get('verdict')!r}")
            continue
        if not r.get("reason_de"):
            problems.append(f"{i}: Begründung fehlt")
        for kind in ("freeware", "payware"):
            item = r.get(kind)
            if item and item.get("url") and not str(item["url"]).startswith("http"):
                problems.append(f"{i}: {kind}-URL ungültig")
            if item and isinstance(item.get("rating"), (int, float)) and not 0 <= item["rating"] <= 5:
                problems.append(f"{i}: {kind}-Bewertung außerhalb 0–5")
        if r["verdict"] == "freeware" and not (r.get("freeware") and r["freeware"].get("url")):
            problems.append(f"{i}: Urteil Freeware ohne Produkt-URL")
        if r["verdict"] in ("optional", "buy") and not (r.get("payware") and r["payware"].get("url")):
            problems.append(f"{i}: Urteil {r['verdict']} ohne Produkt-URL")
        if i in results:
            problems.append(f"{i}: doppelt recherchiert")
        results[i] = r
for i in list(COMBINED) + list(QUALITY_BLOCK) + list(REASON) + list(RATING_SHOWN) + list(CANDIDATE):
    if i not in results:
        problems.append(f"{i}: Sonderregel ohne Rechercheergebnis")
for i in CANDIDATE:
    if i in results and not (results[i].get("freeware") or {}).get("url"):
        problems.append(f"{i}: Kandidat ohne Freeware-Link in der Recherche")
if problems:
    print("Probleme in den Rechercheergebnissen:\n  " + "\n  ".join(problems))
    sys.exit(1)

# Exakte Zahlen aus der zentralen Nachprüfung gegen flightsim.to (vfy/summary.json) haben Vorrang
# vor gerundeten Angaben der Recherche ("ca. 6K").
verified = SRC / "vfy" / "summary.json"
exact = 0
if verified.exists():
    for i, s in json.loads(verified.read_text(encoding="utf-8")).items():
        fw = (results.get(i) or {}).get("freeware")
        if not fw or "id" not in s or f"/{s['id']}/" not in (fw.get("url") or ""):
            continue
        for k, src in (("rating", "rating"), ("count", "count"), ("downloads", "downloads")):
            if s.get(src) is not None and fw.get(k) != s[src]:
                fw[k] = s[src]
                exact += 1

# Frühere Übernahmen dieser Airports entfernen, damit ein erneuter Lauf nichts Veraltetes stehen lässt.
# Von Hand ergänzte Installationsangaben werden gemerkt und unten an denselben Eintrag wieder angehängt.
GENERATED = ("__fw", "__pw", "__cand")
PRESERVE = ("dependencies", "installNote")
kept = {}
for key in [k for k, s in content["scenery"].items() if k.endswith(GENERATED) and s.get("icao") in results]:
    old = content["scenery"].pop(key)
    extra = {f: old[f] for f in PRESERVE if f in old}
    if extra:
        kept[key] = (old.get("url"), extra)
for i in results:
    if str(content["defaultOk"].get(i, "")).startswith("Recherchiert:"):
        del content["defaultOk"][i]
    if i in HAND_LABEL or (results[i]["verdict"] == "handcrafted" and i in content["handcrafted"]):
        content["handcrafted"].pop(i, None)

# ---------- Schwellen anwenden ----------
scenery = content["scenery"]
existing = {}
for key, s in scenery.items():
    existing.setdefault(s.get("icao", key), []).append((key, s))

decisions, deviations, refreshed = {}, [], []
for i, r in results.items():
    v, fw, pw = r["verdict"], r.get("freeware") or {}, r.get("payware") or {}
    if v == "unverified":
        final = "unverified"
    elif v == "handcrafted":
        final = "handcrafted"
    elif fw_ok(i, fw) and i not in QUALITY_BLOCK:
        final = "freeware"
    elif v == "buy" and pw_ok(pw):
        final = "optional"  # Kaufempfehlungen bleiben nach deiner Regel handverlesen
    elif pw_ok(pw):
        final = "optional"
    else:
        final = "stdok"
    decisions[i] = final
    if final != v and not (v == "buy" and final == "optional"):
        why = {
            ("freeware", "optional"): f"{fw_desc(i, fw)} unter der Freeware-Schwelle; {pw_desc(pw)} erfüllt die Payware-Schwelle.",
            ("freeware", "stdok"): f"{fw_desc(i, fw)} unter der Freeware-Schwelle.",
            ("optional", "stdok"): f"{pw_desc(pw)} unter der Payware-Schwelle.",
            ("stdok", "optional"): f"{pw_desc(pw)} erfüllt die Payware-Schwelle.",
            ("optional", "freeware"): f"{fw_desc(i, fw)} erfüllt die Freeware-Schwelle – Freeware hat Vorrang.",
            ("stdok", "freeware"): f"{fw_desc(i, fw)} erfüllt die Freeware-Schwelle.",
        }.get((v, final), "abweichend")
        deviations.append({"icao": i, "research": v, "final": final, "why": why})

    own = existing.get(i, [])
    if final == "freeware":
        scenery[f"{i}__fw"] = {"icao": i, "status": "freeware", "product": fw.get("title"), "dev": fw.get("author") or "",
                               "url": fw["url"], "why": sentence(REASON.get(i) or r["reason_de"]), "rating": fw_rating(i, fw)}
    if final in ("freeware", "optional", "stdok") and pw_ok(pw):
        match = next((s for _, s in own if same_dev(s.get("dev"), pw.get("dev")) or s.get("url") == pw.get("url")), None)
        if match:
            fresh = RATING_SHOWN.get(i) or pw_rating(pw)
            if fresh and fresh != match.get("rating"):
                refreshed.append(f"{i} {match.get('dev')}: {match.get('rating')} → {fresh}")
                match["rating"] = fresh
        elif final == "freeware" or final == "optional":
            scenery[f"{i}__pw"] = {"icao": i, "status": "optional", "product": pw.get("product"), "dev": pw.get("dev") or "",
                                   "url": pw["url"], "rating": pw_rating(pw), "price": short_price(pw.get("price")),
                                   "why": ("Kostenpflichtige Alternative zur Freeware." if final == "freeware"
                                           else sentence(REASON.get(i) or r["reason_de"]))}
    if i in CANDIDATE and final in ("stdok", "optional"):
        scenery[f"{i}__cand"] = {"icao": i, "status": "candidate", "product": fw.get("title"), "dev": fw.get("author") or "",
                                 "url": fw["url"], "why": sentence(CANDIDATE[i]), "rating": fw_rating(i, fw)}
    if final == "handcrafted":
        content["handcrafted"][i] = HAND_LABEL.get(i) or r.get("handcrafted") or "Basis-Sim"
    elif final == "optional":
        dev = pw.get("dev") or "dem Entwickler"
        content["defaultOk"][i] = f"Recherchiert: kein Muss-Add-on; Payware von {dev} als Option."
    elif final == "stdok":
        text = REASON.get(i) or r["reason_de"]
        content["defaultOk"][i] = "Recherchiert: " + sentence(neutral(text))

# Freeware erfüllt die Schwelle, Urteil bleibt wegen Qualitätsbefund
for i, why in QUALITY_BLOCK.items():
    deviations.append({"icao": i, "research": results[i]["verdict"], "final": decisions[i], "why": "Schwelle erfüllt, aber: " + why})

# Gemerkte Installationsangaben wieder anhängen – nur an denselben Eintrag mit demselben Produktlink
preserved, lost = [], []
for key, (url, extra) in kept.items():
    item = scenery.get(key)
    if item is not None and item.get("url") == url:
        item.update(extra)
        preserved.append(key)
    else:
        lost.append(f"{key} ({', '.join(extra)}; Produktlink war {url})")
stale = [f"{i} ist jetzt {decisions[i]}" for i in CANDIDATE if decisions[i] not in ("stdok", "optional")]

counts = {}
for v in decisions.values():
    counts[v] = counts.get(v, 0) + 1
content["research"] = {"date": DATE, "airports": len(results), "rules": RULES + " " + SCOPE.format(airports=len(results))}
print("Ergebnis:", ", ".join(f"{k} {v}" for k, v in sorted(counts.items())), f"· gesamt {len(results)}")
print(f"Exakte flightsim.to-Zahlen übernommen: {exact} Werte")
print("Abweichungen vom Urteil der Recherche:")
for d in deviations:
    print(f"  {d['icao']}: {d['research']} → {d['final']} – {d['why']}")
if refreshed:
    print("Bewertungen eigener Auswahl aktualisiert:\n  " + "\n  ".join(refreshed))
print("Kostenlose Kandidaten (nur zum Prüfen):", ", ".join(k.split("__")[0] for k in scenery if k.endswith("__cand")) or "–")
print(f"Installationsangaben erhalten: {len(preserved)} Einträge")
if lost or stale:
    print("Abbruch – diese Angaben passen nicht mehr zum Ergebnis:\n  " + "\n  ".join(lost + stale))
    print("Angaben prüfen und in content.json bzw. CANDIDATE anpassen, dann neu starten.")
    sys.exit(1)
if DRY:
    print("(Probelauf – nichts geschrieben)")
    sys.exit(0)

content_path.write_text(json.dumps(content, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"geschrieben: {content_path.name}")
if archive_path.exists() and not REPLACE_ARCHIVE:
    print(f"{archive_path.name} bleibt unverändert (damalige Belege); ersetzen nur mit --replace-archive")
else:
    archive_path.write_text(json.dumps(
        {"date": DATE,
         "method": "Je Airport: Handfertigungs-Listen (MSFS-Forum-Guide bis World Update 23, fsnews.eu), FSAddonCompare-Suche, "
                   "flightsim.to-Daten (Suche, Add-on-Details, Kommentare). Freeware-Kandidaten danach zentral gegen "
                   "flightsim.to nachgeprüft (Simulator-Tag, Bewertung, Downloads).",
         "rules": RULES,
         "combined": {i: {"rating": c[0], "count": c[1], "downloads": c[2], "shown": c[3]} for i, c in COMBINED.items()},
         "qualityBlock": QUALITY_BLOCK,
         "candidates": CANDIDATE,
         "deviations": deviations,
         "decisions": decisions,
         "results": results}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"geschrieben: {archive_path.name}")
