# Opus – Ergebnis der Implementierung (24.09.2026)

Geändert: `v2/content.json`, `v2/integrate_research.py`, `v2/build_v2.py`, neu `v2/tests/check_scenery_data.py`.
Nicht angefasst: app.js/app.css/template.html/README, erzeugte Ausgaben, Route, Pflicht-Freeware (VQPR, SCGC, FHSH),
Debriefings, Fortschritt, Originalrecherche (`research-2026-09-24.json`, `work/*`). Nichts heruntergeladen oder installiert.

**Wichtig:** In dieser Sitzung stand mir kein Shell-Werkzeug zur Verfügung. Ich konnte weder Build noch Tests ausführen;
alle Prüfungen unten sind statisch (Gegenlesen, String- und Zählabgleich). Build und `check_scenery_data.py` bitte zuerst laufen lassen.

## 1. Alte Freeware-Fälle → Kandidaten

Primärquellen live geprüft (flightsim.to, 24.09.2026):

| ICAO | Befund | Neu |
|---|---|---|
| VILH | mottoth 4,8 · 3, ~4K DL, v1.0 (5 J.), Tag 2020/2024, keine 2024-Aussage, Absturzmeldung beim Spawnen | `candidate` + `defaultOk`; Sundownersim bleibt `optional` |
| VRMM | NSAJID 4,8 · 4, ~2K DL, v1.1 (19.08.2025), Tag 2020/2024, keine Aussage zu 2024 | `candidate` + `defaultOk` |
| NTTB | kohheiva 4,6 · 5, ~2K DL; laut Autor Watermasks seit SU2 ungenau; braucht 2 superspud-Boots-Libraries | `candidate` (neben `hand` WU13, daher kein defaultOk nötig) |
| LNMC | CDN 5,0 · 7, 1.172 DL, v1.1 (19.04.2026); Triebwerks-Meldung vom Autor zurückgewiesen; keine Pflicht-Abhängigkeit | `LNMC__cand` über `CANDIDATE` in der Integration, `defaultOk` bleibt |

Alle übrigen 18 älteren Freeware-Einträge erfüllen numerisch ≥ 4,5 bei ≥ 8 Bewertungen (Test prüft das). Keine neue Payware.
Texte angepasst, die eine Empfehlung suggerierten: Airport-Briefings VILH/VRMM, Ausflug BORABORA („sonst fehlen Lagune und Riff“ war für 2024 falsch).

## 2. „Angebot recherchiert“ statt „Standard geprüft“

- `integrate_research.py`: Docstring, `RULES`, Abschnittstitel ohne „einheitlich/für alle/Standard geprüft“. Neuer `SCOPE`-Satz nennt die Reichweite:
  289 Recherche-Airports + ältere Freeware; ausgenommen die Kauf-Tipps und 8 bezahlte Beobachtungskandidaten unter der Payware-Schwelle
  (FACT, VNKT, OYSQ, FVFA/FSDG, VQPR/FSDG, NTAA, MMMX, VILH/Sundownersim) – bleiben optional. Test gleicht die Liste mit den Daten ab.
- `neutral()`: „– der Standard reicht“ → „– kein Add-on mit belegtem Mehrwert“ (SBMQ, SBPV, SCTE, SCAT, SPHI), dauerhaft auch beim erneuten Lauf. Skiathos-Briefing ebenso.
- Änderungsliste „Ehrlichkeit“ neu formuliert; Effekt jetzt „72 Freeware-Airports · 87 Optionen · 4 Kandidaten · 0 ungeprüft“
  (72 = 76 Freeware-Airports − LXGB/NTTB als Fix − VILH/VRMM; keiner ist in der Sammlung). Bitte mit der Build-Zeile „Hauptstatus“ gegenprüfen.

## 3. Offene Sim-Existenzprüfungen

`content.simChecks` → `airports[icao].simCheck` für **ZMCK, ZDM, ZZ-0002 (Glorieuses), FMZJ** – alle mit ausdrücklichem Zweifel in unseren Quellen
(ZZ-0002: Ausflugstext „vorab in der MSFS-Weltkarte prüfen“). Nur Status `unconfirmed`. Vorhandene Tipps/Fallbacks unverändert.
Nicht aufgenommen: AD-ALV (Zweifel betrifft nur die Add-on-Zuordnung), SCGC (fehlt laut Autoren im Standard; Pflicht-Freeware liefert die Bahn).

## 4. Installationsabhängigkeiten (Originalseiten, alle Library-Links einzeln verifiziert)

- **RJOO:** `alt` → `dependencies`: Daikichi-Enhancement (WU20, Pflicht, v1.3 vom 24.09.) + Japan airports Model Library KRC (vom Fix verlangt).
- **DNMM:** esosae-Basis (Pflicht, getrennt installieren). **VOCI, KSLC:** KRC (Pflicht). **ELLX:** Datei `pg-ellx-terrainpatch` (Panagiotis28) im Download-Bereich derselben Seite.
- **YPKG:** Korrektur zur Vorgabe – die Super-Pit-Mine steckt im Hauptpaket; das zweite Pflichtpaket ist laut NZA der **Windsack-Patch** (gleicher Download).
- Weitere Pflicht-Libraries: TIST, TBPB, SMJP, EGYP (RAF Lossiemouth ohne deren Abhängigkeiten), MBPV, MMGL (Satellitenbild), PGUM, AYPY, NLWW, OLBA, HAAB, FMCZ, GMMH, DAAG, FMEE (9), ENBO.
- Optional: SUMU (Runway-07/25-Fix), FHAW (Luftbild), HSPN/GBYD (als „Required“ gelistet, laut Autor nur für Flaggen/Personen/Kleinkram).
- `installNote` (25): Variantenwahl (SBBR, OOMS, OSDI, SAWH, FALE, EPKK, NSTU, TKPK), World-Update-/Airport-Bezug (SBCY, SMJP, SEGS, FMCZ, AYPY, NLWW, PGUM, VGHS, OKKK/EICK),
  Konflikte (FMEE: Jetways aus Standard-EDDM, Konflikt mit deiner Aerosoft/SimWings-EDDM; ENBO), EKVG zwei Ordner, TFFF, OLBA, TIST.
- Geprüft ohne Pflichtabhängigkeit: ROAH, VNKT, ENTC, LROP, EYVI, TRPG, MMSD, MMHO, PKMJ, WBSB, WIII, WMKK, OAKB, VOMM, VOGO, VAAH, OERK, LTCG, LTAI, HRYR, FZAA, LIRF, LJLJ, LYBE, LRCL.

## Schema (wie vereinbart)

- Item-Status `candidate`: `product`, `url` (https) Pflicht, nie `required`; der Airport braucht zusätzlich `stdok`/`hand`/… – sonst Build-Abbruch.
- `dependencies: [{product, dev?, url (https), required: bool, note?}]`, nicht leer, keine weiteren Felder. `installNote`: nicht leerer String.
- `content.simChecks[ICAO] = {status: "unconfirmed", note, sources: [https…]}`; ICAO muss in der Tour liegen.
- `build_v2.py`: prüft das alles vor jedem Schreiben; `PRIORITY.candidate = 8` (nie Hauptstatus); `stats.candidate`, `stats.simChecks`; `WELTREISE_CONTENT` für Tests.
- `integrate_research.py`: merkt sich `dependencies`/`installNote` an `__fw/__pw/__cand` und hängt sie bei gleichem Produktlink wieder an – sonst Abbruch statt stillem Verlust.
  Archiv `research-2026-09-24.json` wird nur mit `--replace-archive` überschrieben. Testpfade: `WELTREISE_CONTENT`, `WELTREISE_RESEARCH_OUT`.

## Eigene Prüfungen (statisch)

JSON aller bearbeiteten Stellen gegengelesen; `RULES + SCOPE`, `REASON["LNMC"]`, `CANDIDATE["LNMC"]` zeichengenau mit content.json abgeglichen;
Gedankenstrich/Anführungszeichen per Suche identisch; Zählung 4 candidate · 166 übrige Items · 27 dependencies · 25 installNote · 4 simChecks;
alle Items haben https-Links (neue Validierung weist keine Altdaten ab); Stichprobe: von Hand gepflegte Payware-Bewertungen = Integrationsergebnis.
`python v2/tests/check_scenery_data.py` prüft: 11 Vertragsfehler + Kandidat ohne Urteil werden abgewiesen, Durchreichung, zwei Integrationsläufe
ohne Verlust und ohne Abweichung von content.json, Abbruch bei geändertem Produktlink, Archivschutz. Baut am Ende normal neu (wie check_debriefs.py).

## Offene Punkte

1. **Pflicht-Freeware (laut Vertrag unverändert, Vorschlag):** SCGC-Pack listet „Winter Asset Pack“ als Pflicht (flightsim.to/file/23158, verfügbar);
   VQPR listet Windy Things (laut Autor nur Flaggen); FHSH: bei Navigraph-Navdaten `navdata-fhsh.bgl` löschen. Bitte entscheiden, ob ich das ergänze.
2. TIST: Pflicht-Library „Dave's 3D People Library“ auf flightsim.to 404 (drei Adressen) – keine offizielle Quelle, Spiegelseiten bewusst nicht verlinkt.
3. YPCC, FYWH, FNLU: Seiten lieferten beim Abruf nur den Titel – Abhängigkeiten ungeprüft. Ebenso Detailseiten ZMCK-Freeware und Ascension-Luftbild.
4. Abrufwerkzeug fasst Seiten per Modell zusammen; Labels bei TIST, TBPB, EGYP, FMCZ, MBPV, VOCI u. a. mit V1-Mitschnitten vom 21.09. deckungsgleich.
   Unsichere Zitate habe ich paraphrasiert, widersprüchliche Zeitangaben (NTTB-SU2-Kommentar) weggelassen.
5. Review-Hinweise zu Alttexten (nicht geändert): HAAB-Autor „works only in 2020“ vs. Nutzer; EGYP-Autor „nur in 2020 getestet“ vs. why „Autor bestätigt“;
   EKVG-Briefing sagt „Freeware-Pflicht“, Item ist nicht `required`.
6. Weitere „einen Versuch wert“-Freewares in stdok-Texten (z. B. FZQA, EFMA, HTZA) wären Kandidaten-Anwärter – nicht verifiziert, daher nicht angelegt.
7. Für Astra: README (Status „Angebot recherchiert“, Kandidaten, simChecks, Abhängigkeiten, `--replace-archive`, neuer Test);
   app.js-Zusammenfassung „je Airport geprüft“ im stdok-Block ggf. zu „recherchiert“.
