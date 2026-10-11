# LGSK Skiathos – M'M-Szenerie als Beobachten-Tipp

30.09.2026 · Auftrag des Nutzers direkt an Claude Opus 5.5 (interaktive Sitzung).

M'M Simulations hat am 28./29.09.2026 die erste native MSFS-2024-Szenerie für LGSK veröffentlicht (v1.0.1, ca. 15 € ohne Steuer laut FSAddonCompare). Bewertungen gibt es noch keine. Die Szenerie steht deshalb als bezahlter Beobachtungskandidat unter der Payware-Schwelle da, wie FACT.

## Geänderte Dateien

| Datei | Änderung |
|---|---|
| `v2/content.json` | Szenerie `LGSK` (optional, flightsim.to-Store-Link). Neu geschrieben: `brief` und `defaultOk` von LGSK, die noch „nichts Natives für 2024“ sagten. Regeltext mit LGSK/M'M. Änderungseintrag „Ehrlichkeit“: 88 statt 87 Optionen |
| `v2/integrate_research.py` | `SCOPE` nennt LGSK/M'M. LGSK gehört nicht zum Rechercheauf vom 24.09., der Integrator fasst den Eintrag also nicht an |
| `v2/tests/check_scenery_data.py` | `PAID_WATCH` + LGSK |
| erzeugt | `Volanta-Worldtour-V2.html`, `v2/dist/artifact.html`, `v2/tour-v2.json` |

## Prüfungen

- PASS: `check_scenery_data.py`, `check_debriefs.py`, `check_scenery_ui.cjs`, `check_sync.cjs`.
- **FAIL, schon vorher:** `check_ui_navigation.cjs:67` erwartet 422 Legs, gerendert werden 423. Der Test schlägt auch auf HEAD `d55ae57` ohne diese Änderung fehl und hat damit nichts mit LGSK zu tun. Das bitte klären (Astra): Entweder ist die erwartete Zahl veraltet oder die Liste enthält eine Zeile zu viel.

## Offen

- Hochstufen, sobald es ≥ 10 Bewertungen mit ≥ 4,3 gibt (flightsim.to, Contrail, SimMarket).
- Der Orbx-Link (nur MSFS 2020) steht weiter in `scenery-links.json`, dort nicht angefasst.
- Das Artifact ist nicht neu veröffentlicht. Kein Commit.
