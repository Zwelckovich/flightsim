# Grafiküberarbeitung V2

22.09.2026. Alle zehn ursprünglichen Bildthemen sind in der lokalen Arbeitskopie neu aufbereitet. Acht SVG-Lerntafeln (sieben neu in dieser Runde, Visual Approach aus der vorherigen Runde), zwei strukturierte HTML-Referenzen. V1 und alle zehn eingebetteten Originalbilder bleiben unverändert.

| Thema | Darstellung | Erreichbar |
|---|---|---|
| Cockpit Flow | Unverändertes Quellbild plus lesbare Zonenkarte | Cockpit Prep — Overhead; Sources & V2 Review |
| Anflugtechniken | Vergleich zweier Höhenprofile | Approach — ILS Decelerated |
| Engine Failure after V1 | Steigprofil mit markiertem Beschleunigungsabschnitt | Special Procedures |
| Quick VMC Return | Zusammenhängende Platzrunde in Draufsicht | Special Procedures |
| Circling | Draufsicht, 45°-Offset, Downwind und Landebahn | Special Procedures |
| Visual Approach | Räumliches Flugwegprofil | Special Procedures |
| Touch and Go | Platzrunde und eigener Bahnablauf | Special Procedures |
| Flap Logic | Hebelbefehle und automatische Zustandsübergänge | Referenzen — Flap Logic |
| Emergency Descent | Memory Items und Folgeaktionen getrennt | Special Procedures |
| Overweight Landing | Geordnete Referenz und lesbar gesetzte Quellentabelle | Special Procedures |

## Bedienung

Im Lernmodus erscheint die jeweilige Darstellung über den Schritten. „Grafik vergrößern“ öffnet die SVG mit Zoom, Einpassen, Scrollen und Escape. „SVG speichern“ lädt die einzelne Zeichnung herunter. Jedes Thema bietet einen V1-Originalvergleich. Im Flugmodus bleiben die zusätzlichen Darstellungen ausgeblendet. Die Bilder sind vollständig eingebettet und funktionieren offline.

## Quellen und Grenzen

- [Airbus: Control your Speed — Descent, Approach and Landing](https://safetyfirst.airbus.com/control-your-speed-during-descent-approach-and-landing/?airbus-iframe=true&airbus-post=2130): Vergleich von decelerated und early stabilized, Abbildungen 18–19. VAPP und Landekonfiguration liegen im frühen Verfahren bereits am FDP vor. Die Zeichnung zeigt ein Planungsprofil ohne CDA, keine universelle Festlegung von Einsatzminima oder Stabilisierungskriterien.
- [Airbus: Control your Speed — Climb](https://safetyfirst.airbus.com/control-your-speed-during-climb/?airbus-iframe=true&airbus-post=2145) und [Engine Fire Procedure](https://safetyfirst.airbus.com/do-not-wait-to-apply-the-engine-fire-procedure/?airbus-iframe=true&airbus-post=2080) ergänzen den Engine-out-Quellenkontext. **Der Konflikt zwischen engine securing, maximaler EO ACC und Schubzeitlimit ist nicht vollständig für CFM/Sharklets gelöst.** Im Diagramm bleibt dieser Abschnitt ohne erfundene Grenzwerte. Keine Gleichsetzung von Engine Failure und Engine Fire.
- Cockpit: Die einzige vorhandene Aufnahme ist das kleine, bereits markierte V1-Quellbild. Es wird unverändert neben einer schematischen Zonenkarte gezeigt. Dies ist **kein neuer Fenix-Screenshot** und keine Schalterpositionsreferenz. Rollenbezeichnungen aus V1 wurden nicht in PF/PM umgedeutet.
- Circling, Quick Return, Touch and Go und Flap Logic: Simulator-Trainingsquellen aus den bereitgestellten PDFs. Deren Zahlen werden nicht allein durch eine neue Gestaltung für die konkrete Fenix-Variante validiert.
- Overweight: Zahlen anhand von `pdf-pages/overweight-sheet.png` aus der bereitgestellten Original-PDF übertragen und im Browser abgeglichen. Leere Zellen bleiben leer (Anzeige „—“). Tabelle nur als markierte historische Quelle aufklappbar; keine Berechnung oder Interpolation. Das separate QRH ist A320-232/IAE und hat andere Werte.
- OpenAI Image lieferte zuvor die Gestaltungsstudie für Visual Approach. Die neuen technischen Darstellungen dieser Runde sind kontrollierte SVG-/HTML-Zeichnungen; es wurde kein neuer Bildgenerator-Aufruf als technische Prüfung ausgegeben.

## Prüfung und Pflege

Alle sieben neuen SVGs wurden im Browser angesehen und bei verdeckten Flugwegen, Maßbezügen und Beschriftungen korrigiert. Der Circling-Schwellenmarker folgt der Anflugrichtung. Zoom, Escape, Originalvergleich, Flugmodus und schmale Darstellung wurden geprüft. Die HTML hatte in den geprüften Abläufen keine Konsolenfehler.

`build-plates.cjs` erstellt die sieben neuen SVGs in `plates/` aus kontrollierten Texten und Koordinaten. `plates.json` ordnet Darstellung, Quellen und Originalbild zu. `build-v2.cjs` bettet alle Bilder ein. `verify-v2.cjs` und `verify-graphics.cjs` prüfen Daten, stabile IDs, Einbettung und Erhalt der Originale. Ergebnisse: `TEST_RESULTS.json` und `GRAPHICS_TEST_RESULTS.json`.

Kein Testflug im Fenix. Die bestehenden Quellenlücken sind im Flow und in dieser Dokumentation sichtbar.
