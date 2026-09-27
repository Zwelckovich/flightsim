# Link- und Highlight-Nachprüfung · 25.09.2026

Astra und Claude Opus 5.5 arbeiteten mit Medium Effort. Opus ergänzte die Linkdaten und prüfte Astras Integration; Astra prüfte Opus' Daten, recherchierte Highlights und implementierte Darstellung und Tests. Keine Commits oder Veröffentlichung.

## Ergebnis

- Alle 170 strukturierten Hauptangebote hatten bereits URLs. Ergänzt wurden **343 weitere Verweise für 230 Airports**, vor allem zu im Text erwähnten Alternativen und verworfenen Angeboten. Diese stehen auf Airportkarten und im Szenerien-Reiter, ausdrücklich ohne zusätzliche Kaufempfehlung.
- Drei Suchseiten durch direkte Produktseiten ersetzt: FSIA, HTKJ, DGAA. Der Rechercheimport erhält diese Korrekturen.
- 299 Verweise stammen aus vorhandener Recherche und wurden nicht alle erneut live abgerufen. 40 neue Links recherchierte Opus, davon 25 per Seitenabruf und 15 über Suchtreffer. Astra ergänzte vier weitere Produktseiten (RPMD, LCLK, LMML, VTSP) und prüfte die drei korrigierten FSAddonCompare-Produkte stichprobenartig.
- **46 ausgewählte Highlights: 34 in der Route, 12 fehlen.** Quellen und Anbindungs-Ideen stehen im Highlights-Reiter. Dies ist ein qualitativer Abgleich aus Foren, Medien und Umfragen, keine vollständige Liste oder statistische Messung der Häufigkeit.
- Route unverändert: 422 Legs, 245 Kategorien. Alle Leg-IDs, Start-/Zielairports und Fluggerätklassen gegen Git HEAD verglichen. Kein Fortschritt verändert. Eine spätere Erweiterung der Hauptroute benötigt stabile IDs oder eine Migration.
- Kai Tak bleibt ausgeschlossen. UKLL ist wegen der aktuellen zivilen Luftraumsperre ausdrücklich eine Simulator-Ausnahme. Damit ist die Bestandsroute nicht als ausschließlich aktuell zivil anfliegbar zu bezeichnen. Keine vollständige Live-NOTAM-Prüfung der Bestandsroute.

## Fehlende aktive Highlights

| Airport | Einordnung |
|---|---|
| TNCS · Saba | Hohe Priorität: H160-Ausflug TNCM → TNCS → TNCM. Hubschrauberverkehr ist belegt; H160-Leistung und Szenerie noch im Sim prüfen. Keine Twin Otter nötig, solange der Besuch und nicht das originale STOL-Landeerlebnis das Ziel ist. |
| EGLC · London City | London-Highlight, aber mit den bevorzugten Typen kein regulärer Landestopp: Fenix A320 CFM ist hier nicht zugelassen; eine touristische H160-Landung ist nicht als reguläre Option belegt. Deshalb nur London-Sightseeing als separate Planung, ohne EGLC-Landung. Keine Twin Otter als Ersatz. Einen anderen aktiven Heliport und die Londoner Hubschrauberrouten vor einer Übernahme gesondert prüfen. |
| EGPR · Barra | Hohe Priorität: H160-Ausflug ab EGPE möglich, kein A320. Für das berühmte Rollen und Landen auf dem Strand wäre die Twin Otter eine begründete freiwillige Ausnahme; ein H160-Besuch ersetzt dieses Erlebnis nicht. Gezeiten und Landefläche vorab prüfen. |
| EIDL · Donegal | H160-Ausflug ab EICK oder EGNS. Küstenlinie und Strände machen den Mehrwert aus. Nicht als neuen A320-Sonderfall erzwingen. |
| KSAN · San Diego | Hohe Priorität für den A320: KPHX → KSAN → KLAS statt KPHX → KLAS. Beide neuen Legs bleiben nach Tour-Zeitmodell unter zwei Stunden. Szenerievergleich für den neuen Airport separat erforderlich. |
| KLGA · New York LaGuardia | A320-Highlight. Den Abschnitt KDCA → KJFK gezielt umplanen; ein 10-NM-A320-Sprung KLGA → KJFK wäre wenig sinnvoll. JFK wegen eigener Szenerie erhalten, gegebenenfalls als separater Besuch. Noch keine Routenänderung. |
| LIPZ · Venedig | A320 zwischen LIRF und LFMN möglich; beide Teilstrecken unter zwei Stunden. Gute Ergänzung, aber geringere Priorität als Saba, Barra und San Diego. |
| LIMJ · Genua | A320-Zwischenstopp LIRF → LIMJ → LFMN mit kleinem Umweg. Alternative zu einer größeren Italien-Erweiterung über Venedig. |
| SBSP · São Paulo Congonhas | A320 SBRJ → SBSP → SBFI. Performance auf kurzer Bahn prüfen; kein zusätzlicher Flugzeugtyp nötig. Beide Legs im Zwei-Stunden-Ziel. |
| FSPP · Praslin | Kurzer H160-Ausflug ab FSIA; bietet einen zweiten Blick auf die Seychellen. Für einen A320 ungeeignet, Twin Otter für den Besuch nicht erforderlich. |
| LFLJ · Courchevel | H160-Ausflug ab LSGG; Hubschrauberbetrieb am Altiport ist belegt. Die geneigte Bahn lässt sich besichtigen, das typische Flächenflugzeug-Landeerlebnis wird damit nicht nachgebildet. Hochgebirgsleistung prüfen. |
| LSZS · Samedan | H160-Ausflug ab LSZH oder LOWI. Hubschrauberbetrieb ist belegt; für die Tour kein weiterer A320-Grenzfall. Talroute und Dichtehöhe beachten. |

## Gegenseitige Prüfung

Opus' erste Review steht in `opus-review-astra.md.result.md`. Umgesetzt: keine automatische Hochstufung aller Mediennennungen; ausdrücklich nur St. Barth hervorgehoben. EGLC ohne reguläre A320-/H160-Landung; Hinweis auf nötige ID-Migration bei späterer Routenerweiterung; Klicks innerhalb der Quellenaufklapper öffnen kein Briefing; doppelte Sim-Prüfquellen ausgeblendet; eindeutige VHHH-Quelle statt möglichem Kai-Tak-Beleg; Saba-Betreiberquelle ergänzt; unbenutztes Datenfeld entfernt; doppelte Link-URLs werden vom Build abgelehnt.

Die London-City-Quellen unterscheiden sich in der Formulierung von Hubschrauberausnahmen. Deshalb wird keine touristische H160-Landung behauptet; das reicht für die Tourentscheidung, ohne ein pauschales Verbot sämtlicher Sonderoperationen zu erfinden.

## Tests

PASS: Build, JavaScript-Syntax, `check_links_highlights.py`, `check_scenery_ui.cjs`, `check_ui_navigation.cjs`, `check_sync.cjs` (16 Szenarien), `check_scenery_data.py` (einschließlich zweimaligem Import ohne Verlust). Daten-Negativtests prüfen fehlende/unsichere URLs und geschlossene oder unbelegte Kandidaten. Keine Browser- oder Simulatorprüfung in diesem Auftrag.

## Reproduzierbarer Opus-Aufruf

```powershell
python -X utf8 v2/collaboration/run_opus.py v2/collaboration/2026-09-25-links-highlights/opus-links.md links-20260925 --effort medium
python -X utf8 v2/collaboration/run_opus.py v2/collaboration/2026-09-25-links-highlights/opus-review-astra.md links-highlights-review-20260925 --effort medium --review
python -X utf8 v2/collaboration/run_opus.py v2/collaboration/2026-09-25-links-highlights/opus-final-check.md links-final-20260925 --effort medium --review
```

Der Runner ruft `C:\Users\zwelc\.local\bin\claude.exe -p --model claude-opus-5-5 --effort medium` auf und prüft das tatsächlich initialisierte Modell. Vollständige Tool-/Berechtigungsparameter im Runner. Metadaten und Ereignisprotokolle in `../.runs/`. Claude WebFetch/WebSearch nutzten teilweise Haiku zur Aufbereitung; die beauftragte Arbeit und Reviews liefen auf Opus 5.5. Keine Claude-Unteragenten.

## Abschlussreview

Opus-Nachprüfung: **kein blockierender Befund** (`opus-final-review.md`). Verbleibende kleine Schema-Härtungen sind dort dokumentiert; sie ändern die geprüften Daten nicht.
