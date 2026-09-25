# Karten-Zoom – Übergabe

24.09.2026 · Auftrag des Nutzers direkt an Claude Opus 5.5 (interaktive Sitzung, nicht über `run_opus.py`): „Bau es jetzt ein“ – die Karte soll zoombar sein.

Der Ausgangsstand ist der abgeschlossene UX-Lauf `2026-09-24-ux`: Build 22:19 Ortszeit, B1/B2/B3 freigegeben. Die Zoom-Änderung kam danach. Die dort eingefrorenen Hashes gelten für `app.js`, `app.css`, `template.html` und die erzeugten HTML-Dateien deshalb nicht mehr.

## Geänderte Dateien

| Datei | Änderung |
|---|---|
| `v2/app.js` | siehe unten |
| `v2/app.css` | `.screen:not(.globe) svg` jetzt `touch-action: pan-y` statt `manipulation`: ein Finger scrollt die Seite, zwei Finger gehen an den Kartenzoom statt an den Seitenzoom. Neu: `.zoomctl` (44 px bei `pointer: coarse`), `.zoomhint`, Greifen-Cursor bei `.screen.zoomed` |
| `v2/template.html` | Footer-Hinweis `+ − 0 Karte zoomen` |
| `v2/README.md` | Abschnitt „Karte zoomen“ unter Bedienung |
| erzeugt | `Volanta-Worldtour-V2.html`, `v2/dist/artifact.html`, `v2/tour-v2.json` (per Build) |

Änderungen in `v2/app.js`:

- **Chart-Modul:** Das Modul bekommt `d3.zoom`.
  - Der Zoom wird auf die Projektion angewendet (`scale`/`translate`, beim Globus nur `scale`), nicht als Bildtransformation. Linien, Punkte und Beschriftungen bleiben so gleich groß und die Treffer bleiben anklickbar.
  - Beim Globus bleibt die Rotation beim bestehenden `d3.drag`.
- **Filter:** Mausrad nur mit Strg/⌘ (ohne Strg: kurzer Hinweis, Seite scrollt weiter). Touch nur ab zwei Fingern. Ziehen mit der Maus nur außerhalb des Globus.
- **Bedienelemente:**
  - Knöpfe für Vergrößern, Verkleinern und ganze Ansicht.
  - Das HUD zeigt den Zoomfaktor.
  - In Welt und Globus erscheinen ab 2,5-fach die ICAO-Codes des Kapitels.
- **Zurücksetzen:** Der Zoom beginnt neu bei einem Wechsel von Ansicht oder Kapitel, in der Leg-Ansicht auch bei jedem Leg. Der Globus behält seinen Zoom.
- **Tastatur** im bestehenden globalen Handler: `+`/`=`, `-`, `0`. Die Ausschlüsse aus B2 (Eingabefelder, Tabs, Modifier, nur Body/`.grid`) gelten unverändert.

## Prüfungen

Automatisiert, nach dem Umbau:

- `check_ui_navigation.cjs`, `check_scenery_ui.cjs`, `check_sync.cjs`, `check_scenery_data.py`, `check_debriefs.py`: alle PASS.
- `node --check v2/app.js`: in Ordnung.

Browser (Chromium, `localhost:8000`):

- **Maus und Tastatur:**
  - Strg + Mausrad zoomt und verhindert den Seitenzoom. Das Mausrad allein zoomt nicht, lässt die Seite scrollen und zeigt den Hinweis.
  - Tasten `+ − 0` wirken, im Suchfeld nicht.
  - Die Knöpfe mit Übergang funktionieren. Ziehen verschiebt gezoomt.
  - Legs sind gezoomt anklickbar.
- **Ansichten:**
  - Ein Ansichtswechsel setzt den Zoom zurück.
  - In der Welt erscheinen gezoomt mehr ICAO-Codes.
  - Der Globus wird größer und dreht sich beim Ziehen weiter.
- **Touch-Emulation** (375 px, 5 Touchpunkte):
  - Ein Finger zoomt nicht und blockiert das Scrollen nicht.
  - Zwei Finger zoomen und blockieren den Seitenzoom, auch am Globus.
  - Knöpfe 44 px, kein horizontaler Überlauf.
- **Sichtprüfung:** Karibik in der Welt-Ansicht bei 6,5-fach.

## Offen

- Unabhängige Review nach `M:\flightsim\cowork.md` (Astra).
- Echte Touch-Hardware, Safari und Firefox.
- Das private Online-Artifact ist nicht neu veröffentlicht. Kein Commit.

## SHA-256 dieses Stands

```text
aba6a3c24358ceb9489d90e40fb08485382a47ff1a87403687728d8e93c9041d  v2/app.js
9b1356316ba153592d1c746de20d01b53c7c4d953fca07c6df64617fe2e21483  v2/app.css
f2cbd265e2e658b6a57e44285a0e808a67e930cf3eabb903bbd0a08399911157  v2/template.html
b170d0ea09dd3625e451cfd1bb38fb3574f7a407b815bfbf65f7ad045155dd2b  v2/README.md
49dfa32e98af5ee6778fc8c728c37b9b7359dead40e7fd41efdbaaacc64d13c7  Volanta-Worldtour-V2.html
55cc2fec9dc3dc4b82713fe8f387bcdceb5b820db9b65356ada98ea8597d37c5  v2/dist/artifact.html
```
