# Gezielte Nachprüfung: B1, B2, B3 und kleine Integrationskorrekturen

Projekt M:\flightsim\VolantaWorldTour, Modell Claude Opus 5.5, Effort Max. Nach M:\flightsim\cowork.md. Nur lesen, keine Shell, keine Unteragenten, kein Web, keine Änderungen.

Bitte prüfe ausschließlich die Korrekturen im aktuellen `v2/collaboration/2026-09-24-ux/corrections.diff` an `v2/app.js`, `v2/template.html` und `v2/tests/check_ui_navigation.cjs`. Der vorangegangene unabhängige Review ist in `opus-behavior-review-result.md` desselben Ordners dokumentiert. Keine Wiederholung des Gesamtreviews; der übrige Code ist bereits geprüft.

Der endgültige getestete Stand ist eingefroren: `correction-review-manifest.json`, identisch mit `review-manifest.json`. Code, CSS und generierte HTML-Dateien werden bis zu deiner Übergabe nicht bearbeitet. Das CSS von Opus hat Astra anhand des tatsächlichen Diffs und im Browser separat abgenommen; siehe `astra-review-opus.md`. CSS erneut zu auditieren ist nicht Teil dieses Auftrags.

Korrekturen:
- B1: `reveal` kann ohne Fokuswechsel scrollen. `stepLeg` hält den Fokus auf dem Navigationsbutton, bei neu deaktiviertem Button auf `#jump`. Der native Select behält seinen Fokus nach `change`. Einmalige `openBriefing`-Sprünge fokussieren weiterhin das Briefing.
- B2: Buttons/Links im Briefing erlauben wieder Pfeil/G-Kürzel, Eingaben bleiben ausgeschlossen. Außerhalb des Briefings greifen die Kürzel nur auf body; Tabs/Pips haben eigene Handler.
- B3: Reihenfolge der sichtbaren Checkboxen vor dem Rendern sichern. Fokus auf derselben, sonst folgenden, sonst vorherigen verbleibenden Zeile; leerer Filter auf `#clear-filters`. Kein unbeabsichtigter Suchfokus mehr.
- Suchsprung fokussiert q, scrollt aber zum Anfang von #book, sodass Reiter sichtbar bleiben. Nicht klebende Querformatleiste wird bei der Scrollhöhe nicht abgezogen.
- Ganze erste Tabellenzelle von Zeilennavigation ausgenommen. Sichtbare Formularlabels sind nun auch die zugänglichen Namen, Navigation enthält „Zurück/Weiter“. Benannte Container haben region/group-Rollen.

Unabhängig von Astra bereits ausgeführt und PASS: Build, JS-Syntax, Navigation/Filter-Regressionstest einschließlich neuer B1/B2/B3-Fälle, alle 16 Sync-Szenarien, Szenerie-UI-Test; Daten-/Buildquellen-Hashes unverändert. Browser Chromium auf isoliertem Testursprung: zweimal ArrowDown im Select mit erhaltenem Fokus; zweimal Enter auf Weiter mit erhaltenem Fokus; letzter Flug deaktiviert Weiter und fokussiert Select; Kartenbutton ArrowRight wechselt Leg; Abhaken gefilterter Zeile fokussiert nächsten Treffer, Entfernen des letzten Treffers fokussiert Reset. Der Suchsprung hat gemessen Reiteroberkante 76,95 px bei Navigationsunterkante 60,67 px. Mobile Endabnahme erfolgt zusätzlich durch Astra.

Gib eine knappe Entscheidung: B1/B2/B3 behoben oder konkrete verbleibende Fehler in diesen Korrekturen, mit Datei/Stelle und Reproduktion. Keine neue allgemeine Wunschliste. Unterscheide Befund von lediglich optionalem Komfort. Du hast keine Tests ausgeführt; statische Prüfung klar kennzeichnen. Ziel maximal 350 Wörter für die Übergabe.
