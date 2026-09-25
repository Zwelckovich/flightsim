"""Einmalige Überführung der V2-Daten in die V3-Datenquelle flow-v3.json.

Aufruf:  python v3/migrate_from_v2.py [--force]
Bereits ausgeführt. Ab jetzt ist flow-v3.json die einzige Quelle: Inhalte dort pflegen,
nicht hier. Ohne --force überschreibt das Skript eine vorhandene flow-v3.json nicht.

Was passiert:
- übernimmt die 50 Bereiche und die stabilen Schritt-IDs aus v2/data-v2.json,
- wendet die V3-Änderungen an (jede mit Begründung im Feld "why"),
- ergänzt Anflugarten, After-Takeoff/Climb-Checkliste und vier Weltreise-Karten,
- entfernt Eurowings- und IAE-Inhalte, Fremdgrafiken und V2-Meta-Texte,
- schreibt Änderungsprotokoll und V1/V2/V3-Vergleich für den Reiter „Neu in V3“.
"""
import html
import json
import pathlib
import re
import sys

V3 = pathlib.Path(__file__).resolve().parent
SRC = V3.parent / "v2" / "data-v2.json"
OUT = V3 / "flow-v3.json"
if OUT.exists() and "--force" not in sys.argv:
    sys.exit("flow-v3.json existiert bereits – Inhalte dort pflegen. Neu erzeugen nur mit --force.")

v2 = json.loads(SRC.read_text(encoding="utf-8"))


def md(s):
    """V2-HTML (nur <b>) in schlichtes Markdown-Fett überführen."""
    if s is None:
        return None
    s = re.sub(r"</?b>", "**", str(s))
    return html.unescape(s).strip()


SRC_MAP = {"PROC": "PROC", "FCOM": "FCOM", "USER": "USER", "FENIX": "FENIX", "SIM": "SIM"}
COND_MAP = {"wind": "wind", "takeoff": "toConf", "landing": "ldgConf", "landingMode": "landingMode"}


def conv_item(it):
    label, value, typ = it[0], it[1], it[2]
    m = it[3] if len(it) > 3 and isinstance(it[3], dict) else {}
    d = {"id": m["id"], "item": md(label), "state": md(value), "type": typ, "src": SRC_MAP.get(m.get("s"), m.get("s") or "")}
    if m.get("w"):
        d["caution"] = md(m["w"])
    if m.get("d"):
        d["detail"] = md(m["d"])
    cond = {}
    for k, v in (m.get("condition") or {}).items():
        if k in COND_MAP:
            cond[COND_MAP[k]] = v
    if cond:
        d["when"] = cond
    if m.get("link"):
        d["link"] = m["link"]
    if m.get("revision") == "V2":
        d["rev"] = "v2"
    return d


def conv_section(sec):
    items = []
    for it in sec["items"]:
        if isinstance(it, list):
            items.append(conv_item(it))
        elif "sub" in it:
            items.append({"sub": md(it["sub"])})
        elif "tbl" in it:
            items.append({"table": {"head": it.get("th") or [], "rows": [[md(c) for c in r] for r in it["tbl"]]}})
        # Bilder (img) und Karte (map) entfallen: V3 zeichnet eigene Profile.
    return {"id": sec["id"], "title": md(sec["n"]), "zone": md(sec.get("z")) or "", "note": md(sec.get("note")) or "", "items": items}


phases = {s["id"]: conv_section(s) for s in v2["DATA"]}
kind_of = {"N": "flow", "S": "special", "C": "checklist", "R": "reference"}
for s in v2["DATA"]:
    phases[s["id"]]["kind"] = kind_of[s["g"]]

changes = []  # Einträge für den Reiter „Neu in V3“ (Details)
log = []      # technisches Protokoll pro Schritt


def find(pid, iid):
    for i, it in enumerate(phases[pid]["items"]):
        if it.get("id") == iid:
            return i, it
    raise KeyError(f"{pid}: {iid} nicht gefunden")


def edit(pid, iid, why, **kw):
    _, it = find(pid, iid)
    for k, v in kw.items():
        if v is None:
            it.pop(k, None)
        else:
            it[k] = v
    it["rev"] = "v3"
    log.append({"phase": pid, "id": iid, "action": "geändert", "why": why})


def delete(pid, iid, why):
    i, _ = find(pid, iid)
    del phases[pid]["items"][i]
    log.append({"phase": pid, "id": iid, "action": "entfernt", "why": why})


def insert_after(pid, after_id, why, *items):
    if after_id is None:
        pos = 0
    else:
        pos = find(pid, after_id)[0] + 1
    for k, it in enumerate(items):
        if "id" in it:
            it.setdefault("rev", "v3")
        phases[pid]["items"].insert(pos + k, it)
        log.append({"phase": pid, "id": it.get("id", "(Zwischentitel)"), "action": "neu", "why": why})


def set_sub(pid, old, new):
    for it in phases[pid]["items"]:
        if it.get("sub") == old:
            it["sub"] = new
            return
    raise KeyError(f"{pid}: Zwischentitel {old!r} nicht gefunden")


def step(iid, item, state, typ, src, detail=None, caution=None, when=None, link=None):
    d = {"id": iid, "item": item, "state": state, "type": typ, "src": src}
    if caution:
        d["caution"] = caution
    if detail:
        d["detail"] = detail
    if when:
        d["when"] = when
    if link:
        d["link"] = link
    return d


# ---------------------------------------------------------------- Normal Flow
set_sub("n1", "SIM SETUP — YOUR WORLD TOUR", "SIM SETUP")
edit("n1", "n1.v1-001", "V2-Meta-Text durch eine klare Anweisung ersetzt.",
     detail="Your world-tour aircraft: Fenix A320 CEO with CFM56-5B engines and sharklets. Confirm variant, livery, payload and fuel in the Fenix EFB before powering up.")
insert_after("n1", "n1.v1-001", "Fenix-Einstieg ergänzt: der Flow beginnt Cold & Dark.",
             step("n1.v3-panel", "Fenix EFB — Panel State", "COLD & DARK", "act", "FENIX",
                  detail="The full flow starts from a cold and dark cockpit. If you load a later panel state, mark the power-up steps that are already done as N/A."))

edit("n3", "n3.v1-001", "Konkreter Öl-Richtwert wieder da – mit ehrlicher Quellenangabe statt ersatzloser Streichung.",
     state="≥ 9.5 QT + 0.5 QT/h", detail=(
         "Source procedure (CFM56): minimum 9.5 qt plus an estimated consumption of about 0.5 qt per flight hour — "
         "for a 2-hour leg that is 10.5 qt. Not verified against a CFM56-5B FCOM; treat it as a planning value."))

edit("n4", "n4.v1-012", "Eurowings-Bezug entfernt, FCOM-Regel neutral formuliert.",
     state="NORM · HI IF HOT & HUMID", src="FCOM", detail=(
         "FCOM: LO only with few occupants (fewer than 141 on the A320), HI for abnormally hot and humid conditions. "
         "With a normal passenger load NORM is right. Your 2024 flow simply set the temperature knobs to 12 o'clock."))

edit("n5", "n5.v1-003", "Quelle neutral (war „V2“), Text gestrafft.", src="PROC",
     detail="From the departure clearance and chart — e.g. 5000 ft or FL070. This is independent of the PERF thrust-reduction and acceleration altitudes.")

edit("n6", "n6.v1-007", "Transponder-Hinweis präzisiert.",
     detail="Set the code from the clearance. Without an assigned code the ICAO default is 2000; VFR uses 7000 in Europe and 1200 in the USA.")

edit("n8", "n8.v1-006", "FMS-Vorgabe erklärt, Quelle neutral (war „V2“).", src="PROC", detail=(
    "The FMS proposes a default (usually 1500 ft above the airport). Replace it with the values of the departure or "
    "noise-abatement procedure. The PERF fields are altitudes (ft QNH), not heights above the aerodrome."))
edit("n8", "n8.eo-acc", "Quelle neutral (war „V2“).", src="PROC",
     detail="Engine-out acceleration altitude from the takeoff performance. Brief it together with the maximum acceleration altitude (TOGA time limit).")

edit("n9", "n9.v1-015", "Briefing-Text entschlackt, gleiche Aussage wie die Engine-out-Karte.", caution=None, detail=(
    "Continue. No action below 400 ft AGL except gear up and silencing warnings; then ECAM actions on command. "
    "Level off at the engine-out acceleration altitude once the engine is secured — at the latest at the maximum "
    "acceleration altitude (TOGA time limit). Accelerate, clean up, green dot, MCT; then ECAM, status, relight; "
    "follow the EO routing or an immediate return."))

delete("n11", "n11.v1-009", "IAE-Leerlaufwerte entfernt – V3 ist fest auf CFM56-5B ausgelegt.")
edit("n11", "n11.v1-004", "Nur noch CFM-Angaben.", detail="CFM56 auto-start: igniter at about 16% N2, fuel at about 22% N2, start valve closes at about 50% N2.")

phases["n13"]["note"] = ("FCTM technique: on long straight taxiways let the aircraft accelerate to about **30 kt**, then one smooth brake "
                         "application down to about **10 kt** — fewer, firmer applications save the carbon brakes. Below 10 kt for turns "
                         "of 90° or more. Local and low-visibility limits always apply.")
log.append({"phase": "n13", "id": "(Notiz)", "action": "geändert", "why": "Konkrete FCTM-Taxitechnik statt pauschaler Formulierung."})
edit("n13", "n13.v1-016", "Airline-Name „Taxi-Checkliste“ durch die Airbus-Checkliste ersetzt.",
     item="BEFORE TAKEOFF C/L", state="DOWN TO THE LINE", src="NCL",
     detail="Airbus has one Before Takeoff checklist: the part down to the line during taxi, the rest at line-up.")
edit("n14", "n14.v1-009", "Airline-Name „Line-up-Checkliste“ durch die Airbus-Checkliste ersetzt.",
     item="BEFORE TAKEOFF C/L", state="BELOW THE LINE", src="NCL", detail=None)

phases["n15"]["note"] = ("Captain keeps a hand on the thrust levers until V1. The takeoff-roll technique follows your flight profile: "
                         "standard, or strong crosswind above 20 kt / tailwind.")
set_sub("n15", "STANDARD WIND TECHNIQUE — selected in flight profile", "TAKEOFF ROLL — STANDARD")
set_sub("n15", "STRONG CROSSWIND / TAILWIND TECHNIQUE — selected in flight profile", "TAKEOFF ROLL — CROSSWIND > 20 kt / TAILWIND")
edit("n15", "n15.strong-stabilise", "Quelle ergänzt, Meta-Text entfernt.", src="PROC",
     detail="Let the engines stabilise at 50% before the further increase.")
edit("n15", "n15.strong-brakes", "Quelle ergänzt, Meta-Text entfernt.", src="PROC", detail=None)
insert_after("n15", "n15.v1-020", "Autopilot-Zeitpunkt nach dem Start ergänzt.",
             step("n15.v3-ap", "Autopilot", "AS RQRD — ≥ 100 ft", "act", "FCOM",
                  detail="The AP can be engaged from 100 ft AGL and at least 5 s after liftoff. Follow SRS until then."))

phases["n16"]["note"] = ("Flow first, then the **AFTER TAKEOFF / CLIMB** checklist: down to the line once the flaps are up and the "
                         "packs are on, below the line at the transition altitude.")
log.append({"phase": "n16", "id": "(Notiz)", "action": "geändert", "why": "Die Airbus-Checkliste After Takeoff / Climb existiert und ist jetzt enthalten."})
insert_after("n16", "n16.v1-011", "After-Takeoff/Climb-Checkliste in den Ablauf eingehängt.",
             step("n16.v3-atc1", "AFTER TAKEOFF / CLIMB C/L", "DOWN TO THE LINE", "chk", "NCL", link="c9"))
insert_after("n16", "n16.v1-013", "After-Takeoff/Climb-Checkliste: Teil unter dem Strich an der Transition Altitude.",
             step("n16.v3-atc2", "AFTER TAKEOFF / CLIMB C/L", "BELOW THE LINE", "chk", "NCL", link="c9",
                  detail="Baro reference STD, cross-checked on both sides."))
edit("n16", "n16.v1-013", "V2-Meta-Satz entfernt.", detail="Set STD at the transition altitude and cross-check both sides.")

edit("n18", "n18.v1-009", "Minimum-Felder für alle Anflugarten erklärt.", detail=(
    "Insert the tower wind without gusts — ground-speed mini already covers them. Minimum: the barometric minimum "
    "(DA for ILS CAT I, MDA or DA for non-precision) goes into the MDA field; the DH field is only for CAT II/III radio minima."))
insert_after("n18", "n18.v1-008", "RNAV: Kodierungsprüfung vor dem Anflug.",
             step("n18.v3-coding", "Approach Coding", "CHECK vs CHART", "chk", "FCTM", when={"approach": ["rnav", "npa"]},
                  detail=("Compare the F-PLN from the final approach fix to the missed approach point with the chart: track, "
                          "altitude constraints and final descent angle. Do not modify the final approach segment.")))

edit("n19", "n19.v1-007", "Transition Level als eigenes Datenfeld.", state="FL{{tl}} — SET {{qnhArr}} hPa")

# ---- Anflug: drei Anflugarten als Profil-Zweig
p20 = phases["n20"]
p20["title"] = "Approach"
p20["note"] = ("**ILS and RNAV (FINAL APP):** decelerated approach — CONF 1 and S speed at the final descent point, landing "
               "configuration and VAPP by 1000 ft. **Selected non-precision (TRK/FPA):** early stabilised — landing "
               "configuration and VAPP before the final descent point. Never forget: speed control · approach mode · "
               "configuration points · go-around altitude.")
log.append({"phase": "n20", "id": "(Notiz)", "action": "geändert", "why": "Anflug-Phase deckt jetzt ILS, RNAV (FINAL APP) und NPA (TRK/FPA) ab."})
ILS, RNAV, NPA, DECEL = {"approach": "ils"}, {"approach": "rnav"}, {"approach": "npa"}, {"approach": ["ils", "rnav"]}
edit("n20", "n20.v1-001", "NAV-Genauigkeit inklusive GPS PRIMARY für RNAV.", detail=(
    "NAV ACCURACY HIGH on the PROG page. If it is LOW, at least one ND must show ROSE LS or VOR raw data."))
edit("n20", "n20.v1-002", "Nur im ILS-Zweig; V2-Meta-Text entfernt.", when=ILS,
     detail="Arm when cleared for the approach and on an intercept heading or track. FMA: LOC and G/S blue.")
edit("n20", "n20.v1-003", "Konkrete AP-Regel statt „as briefed“.", when=ILS, state="AS RQRD — BOTH FOR CAT II/III", src="FCOM",
     detail="One AP is enough for a CAT I approach. Autoland and CAT II/III need both APs (CAT 2 / CAT 3 DUAL on the FMA).")
edit("n20", "n20.v1-004", "Nur im ILS-Zweig; Verweis auf die neue Karte „G/S from Above“.", when=ILS,
     detail="Capture from below is the normal case. For a capture from above use the special card “G/S Interception from Above”.")
edit("n20", "n20.v1-007", "Nur im ILS-Zweig.", when=ILS, item="G/S*", detail="After glide-slope capture, set the missed-approach altitude and cross-check it.")
insert_after("n20", "n20.v1-004", "RNAV-Anflug mit FINAL APP ergänzt.",
             step("n20.v3-rnav-gps", "GPS PRIMARY", "CHECK", "chk", "FCOM", when=RNAV,
                  detail="An RNAV (GNSS) approach needs GPS PRIMARY. If GPS PRIMARY is lost before the final descent point, do not continue the RNAV approach unless visual."),
             step("n20.v3-rnav-appr", "APPR pb", "PRESS — FINAL APP ARMED", "act", "FCOM", when=RNAV,
                  detail="Press when cleared and established on — or in NAV towards — the final approach track. FMA: APP NAV green, FINAL blue."),
             step("n20.v3-rnav-vdev", "V/DEV", "MONITOR", "chk", "FCTM", when=RNAV,
                  detail="The vertical-deviation scale on the PFD shows the aircraft relative to the final descent path."),
             step("n20.v3-rnav-final", "FINAL APP", "ENGAGED AT FDP", "chk", "FCOM", when=RNAV,
                  detail="At the final descent point the FMA changes to FINAL APP (green) and the descent starts."),
             step("n20.v3-rnav-ga", "FCU ALT", "SET {{gaAlt}}", "tgt", "FCTM", when=RNAV,
                  detail="Once FINAL APP is engaged and the descent has started, set the missed-approach altitude."),
             step("n20.v3-npa-config", "Landing Configuration", "BEFORE FDP — VAPP", "act", "FCTM", when=NPA,
                  detail="Early stabilised: gear down, landing flaps, ground spoilers armed and VAPP before the final descent point, so the descent starts fully configured."),
             step("n20.v3-npa-trk", "TRK-FPA", "SELECT — BIRD ON", "act", "FCOM", when=NPA,
                  detail="Fly the final track with TRK; the bird on the PFD shows the flight path."),
             step("n20.v3-npa-fpa", "FPA", "{{fpa}}° — PULL 0.2 NM BEFORE FDP", "act", "FCTM", when=NPA,
                  detail="Preset the charted final descent angle and pull it about 0.2 NM before the final descent point so the aircraft joins the path."),
             step("n20.v3-npa-ga", "FCU ALT", "SET {{gaAlt}}", "tgt", "FCTM", when=NPA,
                  detail="Once established in the final descent, set the missed-approach altitude."),
             step("n20.v3-npa-check", "Altitude / Distance", "CHECK vs CHART", "chk", "FCTM", when=NPA,
                  detail="Compare the altitude with the chart's distance table and correct the FPA in small steps (0.1–0.5°)."))
for iid in ("n20.v1-006", "n20.v1-008", "n20.v1-009", "n20.v1-013"):
    edit("n20", iid, "Konfigurationspunkte des Decelerated Approach gelten für ILS und RNAV.", when=DECEL)
edit("n20", "n20.v1-014", "Konfigurationspunkte des Decelerated Approach gelten für ILS und RNAV.", when={"approach": ["ils", "rnav"], "ldgConf": "FULL"})
edit("n20", "n20.conf3-speed", "Quelle ergänzt, Meta-Text entfernt.", src="PROC", detail="Retain CONF 3 and confirm VAPP from the landing performance.")
edit("n20", "n20.v1-017", "Widerspruch zum After-Start-Schritt behoben: Flächenenteisung bei sichtbarem Eisansatz, nicht erst bei starkem.",
     state="AS RQRD", type="cau", src="FCOM", detail=(
         "ON when ice accretion is evident — ice on the visual indicator or the wipers. With significant ice on the airframe "
         "apply the icing corrections of the landing performance."))
edit("n20", "n20.v1-019", "Stabilisierungshöhe nach Airbus; die 1500 ft der Quelle als Betreiberwert markiert.", caution=(
    "Stabilised by **1000 ft** above the airport (500 ft for a visual approach in VMC). Not stabilised → go around."),
    detail=("Criteria: speed +10/−5 kt · pitch +10°/−2.5° · bank 7° · sink rate max 1000 fpm · LOC and glide within ½ dot · "
            "hands on thrust levers and sidestick · briefings and checklists complete. The source procedure uses 1500 ft "
            "for CAT II/III. With more than 10 kt tailwind at landing it does not permit a decelerated approach."))
edit("n20", "n20.v1-021", "CDFA-Hinweis für Nichtpräzisionsanflüge.",
     detail="Non-precision: treat the MDA (plus an add-on, often 50 ft) as a decision altitude — no level-off at MDA (continuous descent final approach).")
edit("n20", "n20.v1-022", "AP-Mindesthöhen nach Anflugart wieder konkret (V2: nur „as briefed“).", state="BY {{apOff}} ft", src="FCOM",
     detail=("A320 minimum AP use heights: ILS with CAT 1 on the FMA 160 ft AGL · FINAL APP, V/S or FPA 250 ft AGL · after a "
             "manual go-around 100 ft. Autoland follows the CAT II/III procedure. Your 2024 flow used 300 ft — a stricter "
             "personal policy, fine to keep."))

# ---------------------------------------------------------------- Sonderverfahren
phases["s1"]["note"] = ("Below 100 kt: reject for any ECAM warning or caution or another significant failure — captain's decision. "
                        "Between 100 kt and V1 be **go-minded** and reject only for the cases below. After V1: continue.")
log.append({"phase": "s1", "id": "(Notiz)", "action": "geändert", "why": "Abbruchkriterien nach Airbus FCTM."})
edit("s1", "s1.v1-004", "Formulierung nach Airbus FCTM.", item="Unable to Fly Safely", src="FCTM",
     detail="Malfunctions or conditions that give unambiguous indications that the aircraft will not fly safely.")
edit("s1", "s1.v1-005", "„Jede ECAM-Meldung“ ersetzt durch rote Warnungen und eine kurze Amber-Liste (Airbus FCTM).",
     item="Red ECAM Warning", src="FCTM", detail="Any red warning. During the takeoff inhibit only a few alerts can appear at all — see the list at the bottom.")
insert_after("s1", "s1.v1-005", "Die wenigen Amber-Cautions, für die Airbus über 100 kt abbricht.",
             step("s1.v3-amber", "Amber: ENG FAIL · REV · THR LVR · SIDESTICK", "REJECT", "wrn", "FCTM",
                  detail="Only these amber cautions: ENG 1(2) FAIL, ENG 1(2) REVERSER FAULT or REVERSE UNLOCKED, ENG 1(2) THR LEVER FAULT, F/CTL SIDESTICK FAULT."))
edit("s1", "s1.v1-006", "Windscherung nur mit Bedingung (Airbus).", state="REJECT — BEFORE V1", src="FCOM",
     detail="Only with significant airspeed variations below V1 and enough runway left to stop.")

edit("s2", "s2.v1-001", "Airbus-Zielwert statt Spanne aus dem Trainingsblatt.", state="ROTATE — 12.5°", src="FCTM",
     detail="Then follow SRS. The simulator sheet gives 10–13°.")
edit("s2", "s2.v1-003", "Reihenfolge korrigiert: erst Seitenruder, dann Trimmung.", state="CENTRE WITH RUDDER · THEN TRIM", src="FCTM",
     detail="Centre the blue beta target with the rudder pedals, then take the pressure off with rudder trim.")
edit("s2", "s2.v1-005", "TOGA-Zeitlimit wieder konkret: 10 min einmotorig, 5 min mit beiden Triebwerken.", src="FCOM",
     caution="TOGA: **10 min** with one engine inoperative, 5 min with all engines (CFM56-5B).",
     detail="The maximum engine-out acceleration altitude in the takeoff performance is based on this limit.")
edit("s2", "s2.v1-008", "Engine-out-Beschleunigung klar formuliert (gleiche Aussage wie das Briefing).",
     item="EO ACC ALT {{eoAcc}}", state="LEVEL OFF · ACCELERATE", src="FCTM",
     caution="Level off once the engine is secured — at the latest at the maximum acceleration altitude (TOGA time limit).",
     detail="Push to level off (or V/S 0), let the speed increase and retract the flaps on schedule. An engine fire is secured with the agent discharged; a failure without damage with the master switch OFF.")

phases["s11"]["note"] = ("Engine start with an external air cart when the APU cannot supply bleed air: engine 2 from the cart, "
                         "engine 1 from the cart as well or by crossbleed.")
phases["s12"]["note"] = "Low-visibility takeoff (LVP, RVR below 400 m) and flying through severe turbulence."
log.append({"phase": "s11", "id": "(Notiz)", "action": "neu", "why": "Kurzbeschreibung ergänzt (war leer)."})
log.append({"phase": "s12", "id": "(Notiz)", "action": "neu", "why": "Kurzbeschreibung ergänzt (war leer)."})
for it in phases["s4"]["items"]:
    it.pop("when", None)
insert_after("s4", None, "Durchstarten und Discontinued Approach stehen beide sichtbar da (kein Profil-Zweig).", {"sub": "GO-AROUND"})
log.append({"phase": "s4", "id": "(Zweige)", "action": "geändert", "why": "Beide Varianten sichtbar – im Moment des Durchstartens wählst du, nicht vorher im Profil."})

edit("s9", "s9.v1-001", "Hinweis ohne Verweis auf das entfernte Bildarchiv.",
     caution="No verified overweight table for the CFM sharklet aircraft is available.",
     detail="Use the landing performance of the Fenix EFB for the actual mass, configuration and conditions.")

# Neue Karten für die Weltreise
NEW_SPECIALS = [
    {"id": "s14", "title": "G/S Interception from Above", "zone": "FCU · PFD", "plate": "gsabove",
     "note": ("Only when cleared for the approach, established on the localizer and with enough distance to be stabilised by "
              "1000 ft. Otherwise ask for vectors or go around."),
     "items": [
         step("s14.v3-01", "APPR pb", "PRESS — LOC · G/S ARMED", "act", "FCTM"),
         step("s14.v3-02", "LOC", "CAPTURED", "chk", "FCTM"),
         step("s14.v3-03", "FCU ALT", "SET ABOVE AIRCRAFT ALTITUDE", "act", "FCTM",
              caution="With the FCU altitude below the aircraft, ALT* would engage before the glide slope is captured."),
         step("s14.v3-04", "V/S", "−1500 fpm (MAX −2000)", "act", "FCTM", detail="Monitor the speed; do not let it run away from the configuration you need."),
         step("s14.v3-05", "Configuration", "GEAR DOWN · FLAPS 2", "act", "FCTM",
              detail="Landing gear and flaps 2 give the best rate of descent. Respect VFE; speed brakes are not recommended below 2000 ft."),
         step("s14.v3-06", "G/S*", "CHECK CAPTURE", "chk", "FCTM"),
         step("s14.v3-07", "FCU ALT", "SET {{gaAlt}}", "tgt", "FCTM"),
         step("s14.v3-08", "1000 ft", "STABILISED — OR GO AROUND", "wrn", "FCTM"),
     ]},
    {"id": "s15", "title": "Hot & High Airports", "zone": "EFB · FMS", "plate": None,
     "note": ("Cusco, La Paz, Quito, Bogotá, Paro, Mexico City, Addis Ababa: high elevation and heat mean high true airspeed, long "
              "distances and less thrust. Performance only from the Fenix EFB with actual temperature, QNH and wind."),
     "items": [
         step("s15.v3-01", "Takeoff Performance", "EFB — ACTUAL OAT · QNH", "act", "FENIX",
              detail="Expect TOGA or a small FLEX margin. Check the engine-out acceleration altitude and the climb gradient against terrain."),
         step("s15.v3-02", "Packs", "OFF or APU BLEED IF REQUIRED", "cau", "PROC", detail="Improves takeoff performance when the EFB needs it."),
         step("s15.v3-03", "Tire Speed", "≤ 195 kt GROUND SPEED", "cau", "FCOM", detail="High true airspeed plus tailwind can reach the tire limit at rotation."),
         step("s15.v3-04", "Engine Start", "WATCH EGT", "cau", "TECH", detail="Thin air means slower light-up and higher EGT — monitor the auto-start closely."),
         step("s15.v3-05", "Terrain", "EO SID · MSA · GRADIENT", "chk", "PROC"),
         step("s15.v3-06", "Landing Performance", "EFB — HIGH GROUND SPEED", "act", "FENIX",
              detail="VAPP stays an indicated speed; the ground speed is much higher. Longer landing distance and more brake energy."),
         step("s15.v3-07", "LDG ELEV", "AUTO — CHECK VALUE", "chk", "FCOM",
              detail="The cabin is scheduled to the airport elevation automatically; after landing the cabin altitude equals the high field elevation."),
         step("s15.v3-08", "Brake Temperature", "MONITOR · ≤ 300 °C FOR T/O", "cau", "FCOM"),
         step("s15.v3-09", "Go-Around", "BRIEF GRADIENT & TERRAIN", "chk", "PROC"),
     ]},
    {"id": "s16", "title": "Short Runway", "zone": "EFB · PEDESTAL", "plate": None,
     "note": ("Funafuti, St Helena, Skiathos: plan the stop before you plan the approach. Landing distance from the EFB with the actual "
              "runway condition, then keep your margin. Your world tour has test legs for Funafuti and St Helena."),
     "items": [
         step("s16.v3-01", "Landing Performance", "EFB — ACTUAL RWY CONDITION", "act", "FENIX"),
         step("s16.v3-02", "Configuration", "CONF FULL", "act", "PROC", detail="Lowest approach speed; CONF 3 only if the performance allows it."),
         step("s16.v3-03", "Auto Brake", "MED or MANUAL", "act", "PROC", detail="LO is for long runways."),
         step("s16.v3-04", "VAPP", "EXACT — NO EXTRA ADDITIVES", "cau", "FCTM", detail="The FMGS already adds the wind correction; every extra knot adds landing distance."),
         step("s16.v3-05", "Aim Point", "TOUCHDOWN ZONE — NO FLOAT", "wrn", "FCTM", detail="A long flare or float is a go-around, not a correction to force onto the runway."),
         step("s16.v3-06", "Reverse", "MAX", "act", "PROC"),
         step("s16.v3-07", "Braking", "AS REQUIRED — FULL IF NEEDED", "act", "PROC"),
         step("s16.v3-08", "Takeoff", "TOGA · PACKS PER EFB", "act", "FENIX"),
         step("s16.v3-09", "Brake Temperature", "≤ 300 °C BEFORE T/O", "cau", "FCOM"),
     ]},
    {"id": "s17", "title": "Cold Weather & Contaminated Runway", "zone": "OVHD · EFB", "plate": None,
     "note": ("Union Glacier and winter stops: treat blue ice and snow as contaminated — performance from the EFB with the correct runway "
              "condition, a reduced crosswind limit and gentle inputs. Union Glacier is a test leg of your world tour."),
     "items": [
         step("s17.v3-01", "Engine Anti-Ice", "ON — OAT ≤ 10 °C + MOISTURE", "act", "FCOM"),
         step("s17.v3-02", "Ice Shedding", "PER FCOM — OAT ≤ +3 °C", "cau", "FCOM", detail="Engine run-ups at intervals during long taxi in freezing fog or precipitation."),
         step("s17.v3-03", "Flaps", "RETRACTED DURING TAXI", "cau", "PROC", detail="With slush or snow keep the flaps up until the holding point."),
         step("s17.v3-04", "Taxi", "SLOW · GENTLE TURNS", "cau", "TECH"),
         step("s17.v3-05", "Takeoff Performance", "EFB — CONTAMINATION", "act", "FENIX"),
         step("s17.v3-06", "Crosswind", "REDUCED LIMIT", "cau", "PROC", detail="Contaminated runways have lower crosswind limits — use the value for the reported runway condition."),
         step("s17.v3-07", "Landing", "AUTO BRAKE MED · MAX REVERSE", "act", "PROC"),
         step("s17.v3-08", "Reversers", "STOW AT 25 kt ON SNOW", "act", "PROC"),
         step("s17.v3-09", "After Landing — Flaps", "CHECK FOR ICE FIRST", "cau", "PROC", detail="After an approach in icing or on a contaminated runway, retract only once the ground crew has checked for ice."),
         step("s17.v3-10", "Fuel Temperature", "MONITOR", "cau", "PROC"),
     ]},
]
for p in NEW_SPECIALS:
    for it in p["items"]:
        it["rev"] = "v3"
    phases[p["id"]] = {"id": p["id"], "kind": "special", "title": p["title"], "zone": p["zone"], "note": p["note"],
                       "items": p["items"], "plate": p["plate"]}
    log.append({"phase": p["id"], "id": "(Karte)", "action": "neu", "why": "Neue Karte für die Weltreise."})

# ---------------------------------------------------------------- Checklisten
c1 = phases["c1"]["items"]
c1.insert(next(i for i, it in enumerate(c1) if it.get("item") == "WINDOWS / DOORS"), {"line": True})
c3 = phases["c3"]["items"]
k = next(i for i, it in enumerate(c3) if it.get("sub") == "AT LINE-UP")
c3[k] = {"line": True, "label": "at line-up"}
c4 = phases["c4"]["items"]
for it in c4:
    if it.get("item") == "BARO / MDA / DH":
        it.update(item="MINIMUM", state="{{mins}} SET (BOTH)", src="NCL", rev="v3")
    if it.get("item") == "BRIEFINGS":
        it["item"] = "BRIEFING"
c4.append({"id": "c4.v3-engmode", "item": "ENG MODE SEL", "state": "AS RQRD", "type": "chk", "src": "NCL", "rev": "v3"})
log.append({"phase": "c4", "id": "c4.v3-engmode", "action": "geändert", "why": "Approach-Checkliste nach Airbus: MINIMUM statt BARO/MDA/DH, ENG MODE SEL ergänzt."})
phases["c9"] = {"id": "c9", "kind": "checklist", "title": "After Takeoff / Climb", "zone": "", "note": "", "items": [
    {"id": "c9.v3-01", "item": "LDG GEAR", "state": "UP", "type": "chk", "src": "NCL", "rev": "v3"},
    {"id": "c9.v3-02", "item": "FLAPS", "state": "RETRACTED", "type": "chk", "src": "NCL", "rev": "v3"},
    {"id": "c9.v3-03", "item": "PACKS", "state": "ON", "type": "chk", "src": "NCL", "rev": "v3"},
    {"line": True, "label": "at transition altitude"},
    {"id": "c9.v3-04", "item": "BARO REF", "state": "STD SET (BOTH)", "type": "chk", "src": "NCL", "rev": "v3"},
]}
log.append({"phase": "c9", "id": "(Checkliste)", "action": "neu", "why": "Airbus After Takeoff / Climb Checkliste ergänzt."})
for cid in ("c1", "c2", "c3", "c4", "c5", "c6", "c7", "c8", "c9"):
    for it in phases[cid]["items"]:
        if "id" in it and it.get("src") == "PROC":
            it["src"] = "NCL"
    phases[cid]["title"] = phases[cid]["title"].upper()

# ---------------------------------------------------------------- Referenz


def table(pid, head0):
    for it in phases[pid]["items"]:
        if "table" in it and it["table"]["head"] and it["table"]["head"][0] == head0:
            yield it["table"]


def set_row(pid, key, value, head0=None):
    for it in phases[pid]["items"]:
        if "table" in it:
            for row in it["table"]["rows"]:
                if row[0] == key:
                    row[1] = value
                    return
    raise KeyError(f"{pid}: Zeile {key!r} nicht gefunden")


def drop_row(pid, key):
    for it in phases[pid]["items"]:
        if "table" in it:
            rows = it["table"]["rows"]
            for i, row in enumerate(rows):
                if row[0] == key:
                    del rows[i]
                    return
    raise KeyError(f"{pid}: Zeile {key!r} nicht gefunden")


def add_row(pid, after_key, row):
    for it in phases[pid]["items"]:
        if "table" in it:
            rows = it["table"]["rows"]
            for i, r in enumerate(rows):
                if r[0] == after_key:
                    rows.insert(i + 1, row)
                    return
    raise KeyError(f"{pid}: Zeile {after_key!r} nicht gefunden")


set_row("r1", "Straight taxiway", "up to about 30 kt (FCTM technique) — local limits apply")
set_row("r1", "Technique", "let it accelerate to ~30 kt, one smooth brake application to ~10 kt")
set_row("r1", "Max TOGA thrust duration", "5 min all engines · 10 min engine out (CFM56-5B)")
set_row("r1", "Thrust reduction altitude", "from the departure procedure, ft QNH (FMS default usually 1500 ft above the airport)")
set_row("r1", "Stabilisation height CAT I", "1000 ft above the airport (500 ft visual in VMC)")
set_row("r1", "Stabilisation height CAT II/III", "1500 ft in the source procedure (operator value)")
set_row("r1", "AP off — non-autoland (limitation)", "ILS with CAT 1 on the FMA: 160 ft AGL")
set_row("r1", "Min AP height, FINAL APP / V/S / FPA", "250 ft AGL")
add_row("r1", "Min AP height, FINAL APP / V/S / FPA", ["Min AP height after takeoff", "100 ft AGL and 5 s after liftoff"])
add_row("r1", "Min AP height after takeoff", ["Minimum fields", "BARO (MDA field): DA or MDA · RADIO (DH field): CAT II/III only"])
add_row("r1", "Brake temp limit for takeoff (fans off)", ["Tire speed limit", "195 kt ground speed"])
drop_row("r3", "Single-engine cruise range, still air")
set_row("r3", "Oil minimum", "9.5 qt + 0.5 qt per flight hour (source procedure, CFM56)")
log.append({"phase": "r1", "id": "(Tabellen)", "action": "geändert", "why": "Konkrete Grenzwerte (Taxi, TOGA, AP-Höhen, Reifen) statt „verify applicable limit“."})
for pid in ("r5", "r6"):
    del phases[pid]
    log.append({"phase": pid, "id": "(Seite)", "action": "entfernt", "why": "Eurowings-Flotte und -Streckenkarte gehören nicht zur Weltreise."})
phases["r4"] = {"id": "r4", "kind": "reference", "title": "Sources", "zone": "", "note": "", "items": [], "sources": True}
for pid, t in (("r1", "Speeds & Limits"), ("r2", "Flap Logic"), ("r3", "Rules of Thumb")):
    phases[pid]["title"] = t
phases["r1"]["note"] = "Values keep their source context. Performance numbers always come from the Fenix EFB for the actual flight."

# ---------------------------------------------------------------- Aufbau & Metadaten
STAGES = [
    {"id": "prep", "title": "Vorbereitung", "phases": ["n1", "n2", "n3", "n4", "n5", "n6", "n7", "n8", "n9"]},
    {"id": "dep", "title": "Abflug", "phases": ["n10", "n11", "n12", "n13", "n14", "n15", "n16"]},
    {"id": "enr", "title": "Reiseflug", "phases": ["n17", "n18"]},
    {"id": "arr", "title": "Ankunft", "phases": ["n19", "n20", "n21"]},
    {"id": "post", "title": "Nach dem Flug", "phases": ["n22", "n23"]},
]
META = {
    "n4": {"plate": "zones"}, "n5": {"plate": "zones", "fields": ["qnhDep", "clearedAlt"]}, "n6": {"plate": "zones", "fields": ["sqk"]},
    "n8": {"fields": ["toConf", "flex", "v1", "vr", "v2", "trim", "thr", "acc", "eoAcc", "ta"]},
    "n9": {"fields": ["toConf", "flex", "v1", "thr", "acc", "eoAcc"]},
    "n10": {"fields": ["v1", "vr", "v2", "flex", "trim"], "checklists": ["c1"]},
    "n12": {"fields": ["toConf", "trim"], "checklists": ["c2"]},
    "n13": {"fields": ["sqk", "toConf"], "checklists": ["c3"]}, "n14": {"checklists": ["c3"]},
    "n15": {"fields": ["wind", "flex", "v1", "vr", "v2"], "plate": "takeoff"},
    "n16": {"fields": ["thr", "acc", "ta"], "plate": "takeoff", "checklists": ["c9"]},
    "n18": {"fields": ["approach", "ldgConf", "landingMode", "qnhArr", "tl", "vapp", "abrk", "mins", "gaAlt", "apOff", "fpa"]},
    "n19": {"fields": ["qnhArr", "tl"], "checklists": ["c4"]},
    "n20": {"fields": ["approach", "ldgConf", "landingMode", "vapp", "mins", "gaAlt", "apOff", "fpa"], "plate": "approach", "checklists": ["c5"]},
    "n22": {"checklists": ["c6"]}, "n23": {"checklists": ["c7", "c8"]},
    "s2": {"fields": ["eoAcc"], "plate": "eo"}, "s3": {"plate": "quickreturn"}, "s4": {"fields": ["gaAlt"], "plate": "goaround"},
    "s6": {"plate": "circling"}, "s7": {"plate": "visual"}, "s14": {"fields": ["gaAlt"]},
}
for pid, m in META.items():
    phases[pid].update(m)

FIELDS = [
    {"id": "qnhDep", "label": "QNH", "unit": "hPa", "group": "dep", "hint": "1013"},
    {"id": "clearedAlt", "label": "FCU ALT", "unit": "", "group": "dep", "hint": "5000 / FL070"},
    {"id": "sqk", "label": "SQUAWK", "unit": "", "group": "dep", "hint": "2000"},
    {"id": "flex", "label": "FLEX", "unit": "°C", "group": "dep", "hint": "45"},
    {"id": "v1", "label": "V1", "unit": "kt", "group": "dep", "hint": "140"},
    {"id": "vr", "label": "VR", "unit": "kt", "group": "dep", "hint": "142"},
    {"id": "v2", "label": "V2", "unit": "kt", "group": "dep", "hint": "146"},
    {"id": "trim", "label": "THS", "unit": "", "group": "dep", "hint": "UP0.8"},
    {"id": "thr", "label": "THR RED", "unit": "ft", "group": "dep", "hint": "1500"},
    {"id": "acc", "label": "ACC", "unit": "ft", "group": "dep", "hint": "1500"},
    {"id": "eoAcc", "label": "EO ACC", "unit": "ft", "group": "dep", "hint": "1500"},
    {"id": "ta", "label": "TRANS ALT", "unit": "ft", "group": "dep", "hint": "5000"},
    {"id": "qnhArr", "label": "QNH", "unit": "hPa", "group": "arr", "hint": "1013"},
    {"id": "tl", "label": "TRANS LVL", "unit": "FL", "group": "arr", "hint": "70"},
    {"id": "vapp", "label": "VAPP", "unit": "kt", "group": "arr", "hint": "138"},
    {"id": "abrk", "label": "A/BRK", "unit": "", "group": "arr", "hint": "LO"},
    {"id": "mins", "label": "MINIMUM", "unit": "ft", "group": "arr", "hint": "DA 580"},
    {"id": "gaAlt", "label": "GA ALT", "unit": "", "group": "arr", "hint": "5000"},
    {"id": "apOff", "label": "AP OFF", "unit": "ft", "group": "arr", "hint": "300"},
    {"id": "fpa", "label": "FPA", "unit": "°", "group": "arr", "hint": "-3.0", "when": {"approach": "npa"}},
]
PROFILE = [
    {"id": "wind", "label": "STARTLAUF", "options": [["normal", "Standard"], ["strong", "X-Wind > 20 kt / Rückenwind"]], "default": "normal"},
    {"id": "toConf", "label": "T/O CONF", "options": [["1", "1+F"], ["2", "2"], ["3", "3"]], "default": "1"},
    {"id": "approach", "label": "ANFLUG", "options": [["ils", "ILS"], ["rnav", "RNAV · FINAL APP"], ["npa", "NPA · TRK/FPA"]], "default": "ils"},
    {"id": "ldgConf", "label": "LDG CONF", "options": [["FULL", "FULL"], ["3", "3"]], "default": "FULL"},
    {"id": "landingMode", "label": "LANDUNG", "options": [["manual", "Manuell"], ["autoland", "Autoland"]], "default": "manual"},
]
SOURCES = {
    "FCOM": {"label": "FCOM", "text": "Airbus Flight Crew Operating Manual – Inhalt nach der Verfahrensquelle bzw. Airbus-Standard, nicht Zeile für Zeile gegen ein FCOM des CFM-Sharklet-Musters geprüft."},
    "FCTM": {"label": "FCTM", "text": "Airbus Flight Crew Techniques Manual – empfohlene Technik, nach Airbus-Standard zusammengefasst."},
    "NCL": {"label": "NCL", "text": "Airbus Normal Checklist – Aufbau mit Strich (down to the line / below the line)."},
    "QRH": {"label": "QRH", "text": "Vorliegendes QRH (EC-MLE, A320-232/IAE, März 2016) – nur für Wortlaut und Bedingungen, nicht für Leistungswerte."},
    "PROC": {"label": "PROC", "text": "A320 Normal Procedures (TheAirlinePilots) – betreiberlastige, FCOM-basierte Zusammenstellung; Hauptquelle von V1."},
    "SIM": {"label": "SIM", "text": "Simulator-Trainingsblätter (u. a. FSLabs) – nur für die Simulation, Übertragbarkeit auf den Fenix nicht belegt."},
    "FENIX": {"label": "FENIX", "text": "Fenix-/MSFS-spezifische Bedienung – kein Verfahren des echten Flugzeugs."},
    "USER": {"label": "DEIN FLOW", "text": "Aus deinem Flow von 2024 übernommen."},
    "TECH": {"label": "TECHNIK", "text": "Für die Weltreise zusammengefasste Technik (V3) – aus den Verfahren oben abgeleitet; Leistung immer aus dem EFB."},
}

ORDER = ([f"n{i}" for i in range(1, 24)] + [f"s{i}" for i in range(1, 18)]
         + [f"c{i}" for i in range(1, 10)] + ["r1", "r2", "r3", "r4"])
out_phases = []
for pid in ORDER:
    p = phases[pid]
    q = {"id": pid, "kind": p["kind"], "title": p["title"], "zone": p.get("zone", ""), "note": p.get("note", "")}
    for k in ("fields", "plate", "checklists", "sources"):
        if p.get(k):
            q[k] = p[k]
    q["items"] = p["items"]
    out_phases.append(q)
assert len(out_phases) == len(phases), "Bereiche nicht vollständig geordnet"

n_steps = sum(1 for p in out_phases for it in p["items"] if "id" in it)
COMPARE = [
    ["Bereiche", "50", "50", str(len(out_phases))],
    ["Abhakbare Schritte", "605", "609", str(n_steps)],
    ["Checklisten", "8", "8", "9 – mit After Takeoff / Climb"],
    ["Sonderverfahren", "13", "13", "17 – vier neue für die Weltreise"],
    ["Anflugarten im Normal-Flow", "ILS", "ILS", "ILS · RNAV (FINAL APP) · NPA (TRK/FPA)"],
    ["Flugdaten beim Fliegen", "Kopfleiste", "hinter einem Dialog", "pro Phase im Briefing"],
    ["Grafiken", "10 Fremdbilder", "10 Fremdbilder + 8 helle Tafeln", "9 eigene, dunkle Grafiken – Profile mit deinen Werten"],
    ["Dateigröße", "1,0 MB", "3,4 MB", "rund 235 KB"],
    ["Quellen", "pauschal", "pro Schritt", "pro Schritt, mit Legende"],
    ["Eurowings / IAE", "ja", "teilweise", "nein"],
    ["Datenquelle", "im HTML", "V1-HTML + Patch-Skript", "flow-v3.json"],
]
CHANGES = [
    {"area": "Inhalt", "title": "V2-Korrekturen übernommen",
     "text": "Getrennte FCU-Freigabehöhe, THR RED/ACC nach Abflugverfahren, kein Ersatz-CG, Fahrwerk pro Bein, Fuel-Check am gleichen Punkt, Engine-out ohne Widerspruch, 7700 mit Bedingung, Touch-and-go-Reihenfolge.",
     "effect": "alle echten V2-Fixes"},
    {"area": "Inhalt", "title": "Konkrete Werte zurück",
     "text": "Wo V2 korrekte Zahlen durch „as briefed“ ersetzt hat, stehen sie wieder da – mit Quelle: Taxi 30 → 10 kt (FCTM), AP-Mindesthöhen 100/160/250 ft, TOGA 5/10 min, Öl 9,5 qt + 0,5 qt/h.",
     "effect": "brauchbar im Cockpit"},
    {"area": "Fehler", "title": "After Takeoff / Climb",
     "text": "V1 behauptete, die Checkliste gebe es nicht mehr; V2 räumte ein, dass es sie gibt, ließ sie aber weg. Sie ist jetzt da und im Flow eingehängt.",
     "effect": "9 Checklisten"},
    {"area": "Fehler", "title": "Startabbruch nach Airbus",
     "text": "Zwischen 100 kt und V1 nicht mehr „jede ECAM-Meldung“, sondern Feuer, schwere Schäden, Schubverlust, Flugunfähigkeit, rote Warnungen und fünf bestimmte Amber-Cautions.",
     "effect": "go-minded"},
    {"area": "Fehler", "title": "Anflug ohne Widersprüche",
     "text": "Wing Anti-Ice bei sichtbarem Eisansatz statt „nur bei starker Vereisung“; Stabilisierung 1000 ft (500 ft visuell); die 1500 ft der Quelle als Betreiberwert markiert.",
     "effect": "konsistent"},
    {"area": "Weltreise", "title": "Drei Anflugarten",
     "text": "Der Normal-Flow kennt jetzt ILS, RNAV mit FINAL APP und Nichtpräzisionsanflüge mit TRK/FPA – umgeschaltet im Flugprofil, mit CDFA-Hinweis und Kodierungsprüfung.",
     "effect": "für Inseln und Berge"},
    {"area": "Weltreise", "title": "Vier neue Karten",
     "text": "G/S von oben, Hot & High (Cusco, La Paz, Quito …), kurze Bahnen (Funafuti, St Helena …) sowie Kälte und kontaminierte Bahn (Union Glacier).",
     "effect": "17 Sonderverfahren"},
    {"area": "Aufgeräumt", "title": "Eurowings und IAE entfernt",
     "text": "Flottenseite, Streckenkarte, Pack-Flow-Bezug und IAE-Leerlaufwerte sind raus; V3 ist auf den Fenix A320 CEO mit CFM56-5B und Sharklets ausgelegt.",
     "effect": "ein Flugzeug"},
    {"area": "Design", "title": "Im Look der Weltreise",
     "text": "Gleiche Farben, Schriften und Bausteine wie die Weltreise V2: Phasen-Leiste über den ganzen Flug, Briefing links, Schritte und Profil rechts, Tracks und Reiter.",
     "effect": "eine Familie"},
    {"area": "Technik", "title": "Eine Datenquelle",
     "text": "Alle Inhalte stehen in flow-v3.json und werden per build_v3.py zur Offline-Datei. Die stabilen Schritt-IDs aus V2 bleiben – Häkchen überleben Änderungen.",
     "effect": "wartbar"},
]

data = {
    "meta": {"title": "Fenix A320 Flow", "version": "V3", "date": "2026-09-24",
             "aircraft": "Fenix A320 CEO · CFM56-5B · Sharklets",
             "scope": "Persönliche Simulator-Hilfe für den Fenix A320 in MSFS 2024 – kein Airline-SOP, nicht für den echten Flugbetrieb.",
             "basis": "V2 (Astra) mit stabilen IDs, Inhalt ursprünglich aus V1 (Fable) und deinem Flow von 2024."},
    "sources": SOURCES, "fields": FIELDS, "profile": PROFILE, "stages": STAGES,
    "phases": out_phases, "compare": COMPARE, "changes": CHANGES, "log": log,
}
OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"geschrieben: {OUT.name} · {len(out_phases)} Bereiche · {n_steps} Schritte · {len(log)} Protokolleinträge")
