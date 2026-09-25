# Weltreise ab Weeze – V2

Die überarbeitete Tour: **388 A320-Legs + 17 H160-Ausflüge (34 Legs), rund 450 h, alle 245 Volanta-Kategorien, keine Twin Otter, nur aktive Flughäfen.**

## Öffnen

- **Lokal:** `../Volanta-Worldtour-V2.html` direkt im Browser öffnen. Funktioniert offline (Karte und Daten eingebettet). Fortschritt liegt im Browserspeicher; über „Fortschritt sichern“ als JSON exportieren.
- **Überall (Tablet neben dem Sim):** das private Artifact „Weltreise ab Weeze“ auf claude.ai. Dort wird der Fortschritt in der Artifact-Datenbank gespeichert und zwischen Geräten synchronisiert. Claude kann ihn beim Debriefing mitlesen.

Eine V1-Sicherung (Export aus der alten HTML) lässt sich über „Sicherung laden“ importieren – passende Strecken werden automatisch abgehakt.

## Bedienung

Die Leg-Navigation bleibt am oberen Rand erreichbar. „Erstes offenes Leg“ führt zum ersten noch nicht abgehakten Flug der gesamten Tour; „Leg suchen“ öffnet den Flugplan und setzt den Fokus in die Suche. Die Leg-Auswahl zeigt auch den Zielort und zählt A320- und H160-Etappen gemeinsam. Unter „Gesamte Route“ lassen sich die Kapitel und nummerierten Legs aufklappen.

Die Suche kombiniert mehrere Begriffe (z. B. `EDLV EHAM`) und findet Ortsnamen auch ohne Akzente (`Reykjavik`). Zusätzlich zu den Volanta-Namen werden deutsche Ländernamen wie `Deutschland` erkannt. Status und Kapitel lassen sich zusätzlich filtern; „Filter zurücksetzen“ stellt alle 422 Legs wieder her. Die Strecken im Flugplan und die Leg-Buttons der Szenerielisten öffnen das zugehörige Briefing.

Tastatur: In den Reitern wechseln Links/Rechts sowie Pos1/Ende den Bereich. In der aufgeklappten Route wechseln die Pfeile das Leg. Im Briefing blättern Links/Rechts durch die Legs und `G` ändert den Geflogen-Status, auch bei fokussierten Briefing-Buttons. `+`, `−` und `0` zoomen die Karte bzw. zeigen wieder die ganze Ansicht. Eingabefelder und Bedienelemente außerhalb des Briefings lösen diese globalen Kürzel nicht aus. Die obere Leg-Auswahl und Zurück/Weiter behalten ihren Fokus für wiederholtes Blättern.

Karte zoomen:

- **Maus:** `Strg` + Mausrad (Mac: `⌘`) oder die Trackpad-Geste zoomt; das Mausrad allein scrollt weiter die Seite und blendet einen kurzen Hinweis ein. Gezoomt verschiebt Ziehen den Ausschnitt, Doppelklick vergrößert (mit Umschalt: verkleinert).
- **Touch:** zwei Finger zoomen und verschieben, ein Finger scrollt weiter die Seite.
- **Knöpfe** oben rechts in der Karte: vergrößern, verkleinern, ganze Ansicht.
- Gezoomt wird die Projektion, nicht das Bild: Linien, Punkte und ICAO-Beschriftungen bleiben scharf und gleich groß, Legs und Flughäfen bleiben anklickbar.
- In Welt und Globus erscheinen ab etwa 2,5-fachem Zoom die ICAO-Codes aller Flughäfen des aktuellen Kapitels.
- Der Globus wird beim Zoomen größer und lässt sich weiter ziehen.
- Ein Wechsel der Ansicht oder des Kapitels, in der Leg-Ansicht auch jedes neue Leg, beginnt wieder mit der ganzen Ansicht. Der Globus behält seinen Zoom.

## Neu bauen

```powershell
python v2/build_v2.py
```

Voraussetzung: Python 3. Der Build prüft Kapitel-Übergänge, geschlossene Flughäfen und die Abdeckung aller 245 Kategorien und bricht bei Fehlern ab.

| Datei | Inhalt |
|---|---|
| `route.json` | Kapitel mit Airport-Reihenfolge und H160-Ausflüge – hier wird die Route geändert |
| `content.json` | Highlights, Briefings, Szenerie-Empfehlungen, Ausflugstexte, Änderungsliste |
| `debriefings.json` | Debriefing-Archiv für Git (Schema wie V1, Leg-IDs `L001` … bzw. `X-GG-1`) |
| `template.html`, `app.css`, `app.js` | Seite, Farbschema (aus `walkthrough.build.html`) und Logik |
| `research-2026-09-24.json` | Szenerie-Recherche aller Airports: Rohdaten, Quellen, Regeln, Abweichungen |
| `integrate_research.py` | übernimmt Rechercheergebnisse nach den einheitlichen Schwellen in `content.json` |
| `tour-v2.json` | erzeugte Daten (nicht von Hand bearbeiten) |
| `dist/artifact.html` | erzeugtes Artifact-Fragment (d3 per CDN) |

Die Grunddaten (OurAirports, Natural Earth, d3) kommen aus `../work/`.

## Debriefing nach jedem Leg

Wie in V1: nach dem Flug im Chat erzählen, welche Szenerien tatsächlich aktiv waren. Claude schreibt den Bericht in `debriefings.json` (Git) und zusätzlich in die Artifact-Datenbank (Collection `debriefs`, Dokument-ID = Leg-ID) – dann erscheint er sofort in der Online-Version, ohne Neuveröffentlichung. In der Seite gibt es pro Leg eine kopierbare „Debrief-Vorlage“.

## Fortschritt, Volanta-Status und Reset

- **Häkchen** werden pro Leg mit Zeitstempel gespeichert, auch entfernte. Beim Verbinden mit der Cloud gewinnt pro Leg die neuere Änderung; nichts Lokales wird verworfen.
- **Laufender Abgleich:** Neue Cloud-Änderungen werden als einzelne Einträge erhalten. Dadurch kann eine verspätete ältere Änderung den neueren Stand auch dann nicht überschreiben, wenn dessen Gerät bereits geschlossen ist. Gleiche Zeitstempel werden auf allen Geräten gleich aufgelöst. Lokale Änderungen berücksichtigen bereits empfangene spätere Zeitstempel. Ältere Cloud-Einträge und Sicherungen bleiben lesbar; für den neuen Abgleich bitte die aktualisierte HTML auf allen Geräten verwenden.
- **Kategorien:** „laut Flugplan erreicht“ (aus den Häkchen) ist getrennt von „in Volanta bestätigt“ bzw. „nicht gewertet“. Den Volanta-Status setzt du im Reiter *Kategorien* an der Kachel, oder er kommt aus dem Debriefing (`volanta: credited / not_credited`).
- **Reset** unter *Daten & Reset*: Häkchen, Volanta-Status und – in der Online-Version – die Cloud-Debriefings, jeweils mit Rückfrage und Sicherungsangebot. Ein Reset gilt auf allen synchronisierten Geräten. Das Git-Archiv `debriefings.json` bleibt als Tagebuch erhalten; Volanta-Angaben aus Debriefings, die vor einem Volanta-Reset erfasst wurden, zählen danach nicht mehr.
- **Sicherung laden** ergänzt: Was in der Sicherung geflogen bzw. bestätigt war, wird als neue Änderung übernommen – auch nach einem Reset. Bereits geflogene Legs bleiben.
- **Debriefings** trage ich mit `volantaAt` (Zeitpunkt der Volanta-Angabe, ISO-Format) ein, damit ein späterer Volanta-Reset sie korrekt einordnet.

## Tests

```powershell
python v2/tests/check_debriefs.py      # Archivprüfung: 10 Fehlerfälle, 1 gültiges Archiv
python v2/tests/make_sync_tests.py     # erzeugt v2/tests/out/*.html
node v2/tests/check_sync.cjs           # isolierte Sync-Regressionen, ohne echte Cloud/Browserdaten
node v2/tests/check_scenery_ui.cjs     # Darstellung von Abhängigkeiten, Kandidaten und Sim-Prüfungen
node v2/tests/check_ui_navigation.cjs  # Suche, kombinierte Filter, Reiter-Tastatur und Navigationsgrenzen
python v2/tests/check_scenery_data.py  # Datenvertrag, Metadaten-Erhalt und wiederholbare Integration
```

Die Seiten in `v2/tests/out/` (z. B. über `python -m http.server` öffnen) spielen je ein Szenario mit simulierter Cloud durch und zeigen oben PASS oder FAIL: Zusammenführen lokal/Cloud, zweites Gerät nach Reset, Sicherung nach Reset, altes Cloud-Format mit und ohne späteren Reset, Volanta-Reset mit Debriefing, verspätete Änderungen nach Schließen des neueren Geräts und unabhängige Reset-Einträge. Es werden acht Seiten erzeugt.

Die 16 Node-Sync-Szenarien und der Renderingtest laufen mit isolierten Speicher- und Cloud-Mocks. Sie prüfen Logik und erzeugtes Markup; einen visuellen Browserlauf oder einen Test gegen die private Artifact-Datenbank ersetzen sie nicht.

## Szenerie-Status

`Eigene` · `Kauf-Tipp` · `Freeware` · `Handgefertigt` · `Angebot recherchiert` (Add-on-Angebot geprüft, keine Aussage über einen eigenen Sim-Test) · `Optional` (Payware) · `Freeware · prüfen` (Beobachtungskandidat) · `Ungeprüft` (Recherche offen).

Die Angebotsrecherche liegt für jeden Airport der Tour vor (Stand 24.09.2026: FSAddonCompare, flightsim.to und die Listen handgefertigter Airports bis World Update 23). Die Recherche über 289 Airports verwendet folgende Schwellen als Vorauswahl; aktuelle Einschränkungen und ältere Einzelentscheidungen stehen zusätzlich beim jeweiligen Produkt:

- **Freeware:** ab 4,5 Sternen bei mindestens 8 Bewertungen oder 6.000 Downloads und belegtem MSFS-2024-Betrieb (Tag auf flightsim.to, Aussage von Autor oder Nutzern). Getrennte 2020-/2024-Einträge derselben Szenerie zählen zusammen.
- **Optional (Payware):** ab 4,3 Sternen bei mindestens 10 Bewertungen und MSFS-2024-Angabe. Dazu kommen wenige handverlesene Beobachtungskandidaten mit eigener Begründung (z. B. einzige Umsetzung, noch unbewertet).
- **Angebot recherchiert:** keine feste Add-on-Empfehlung, jeweils mit Begründung. Ein Qualitätsbefund (veraltetes Layout, Fehler in 2024) kann eine Empfehlung trotz Schwelle verhindern. Fehlende Bewertungen beweisen keine schlechte Qualität und bestätigen auch nicht die Qualität des Standards.
- **Freeware · prüfen:** interessante kostenlose Kandidaten ohne ausreichenden Empfehlungsbeleg. Sie stehen separat und gehören nicht in die empfohlenen Downloads.
- **Sim-Prüfung offen:** Existenz oder Nutzbarkeit eines Landeplatzes im Simulator ist noch unbestätigt. Dies ist unabhängig davon, ob bereits nach Add-ons gesucht wurde.

Die Kapitel-Downloadlisten enthalten auch hinterlegte Pflichtbestandteile, optionale Ergänzungen und Installationshinweise. Beobachtungskandidaten bleiben außerhalb dieser empfohlenen Liste.

Die ursprünglichen Rohdaten und damaligen Entscheidungen bleiben in `research-2026-09-24.json` erhalten. Die Nachprüfung und anschließenden Änderungen dokumentiert `collaboration/2026-09-24/`. Übernahme neuer Rechercheergebnisse: `python v2/integrate_research.py <Ordner> --dry` (Probelauf), danach ohne `--dry` und neu bauen. Installationsangaben bleiben beim selben Produkt erhalten; bei einem Produktwechsel bricht das Skript zur manuellen Prüfung ab. Ein bestehendes Recherchearchiv wird nur mit `--replace-archive` ersetzt.

## Sonderetappen

Funafuti (NGFU), Union Glacier (SCGC) und St Helena (FHSH) liegen außerhalb des realen A320-Betriebs. Sie haben in der Seite eine Testcheckliste und einen Ausweichplan – vorher im Freeflug und im Fenix-EFB prüfen.

## Vor dem Losfliegen prüfen

- **Nuuk (BGGH):** eigene M'M-Szenerie auf v1.1.0 aktualisieren (neue 2.200-m-Bahn). Der MSFS-Standard ist dort unbrauchbar.
- **Pflicht-Freeware:** Antarctica Airfield Pack (Union Glacier fehlt sonst), St. Helena von kychungdotcom (inkl. Navdaten), Paro von kychungdotcom.
- **Ulaanbaatar (ZMCK):** Der neue Flughafen (eröffnet 2021) fehlt in MSFS 2020; ob MSFS 2024 ihn enthält, ist nicht belegt. Vor Kapitel 14 in der Weltkarte suchen. Fehlt er: Hohhot → Ulan-Ude direkt (682 NM, 2:00 h) – die Mongolei zählt ohnehin über Chowd (ZMKD).
- **Volanta-Wertung vorab ansehen:** Glorieuses (Französische Südgebiete) und Ramallah Heliport (Palästina) sind neu gegenüber V1. Falls Volanta sie nicht wertet: Juan de Nova (FMZJ) ab Mayotte bzw. Bethlehem Heliport als Ausweichziel.

## Zusammenarbeit Astra / Opus

Der gemeinsame Arbeitslauf vom 24.09.2026 ist unter `collaboration/2026-09-24/README.md` dokumentiert. `collaboration/run_opus.py` startet begrenzte Implementierungs- oder Review-Aufträge mit **Claude Opus 5.5, Max Effort**. Modell, Aufträge und Reviews sind nachvollziehbar; die laufenden CLI-Protokolle liegen im ignorierten Ordner `collaboration/.runs/`. Die Aufteilung verhindert gleichzeitige Änderungen an denselben Quelldateien.
