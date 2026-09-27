# Review: Astras Link- und Highlight-Integration

**Ergebnis:** Nichts blockiert den eingefrorenen Stand. Route, IDs und XSS-Schutz sind in Ordnung. Zwei Punkte sollten aber vor der Freigabe entschieden werden: das pauschale Hochstufen auf `level = 2` und die EGLC-Einordnung.

## Was ich bestätigen kann

- **Zählung stimmt:** 46 Einträge, davon 34 in der Route und 12 fehlend. Keiner der 12 steht im Airport-Verzeichnis von `tour-v2.json`.
- **Anschlüsse vorhanden:** Die Legs, auf die sich die Vorschläge beziehen, gibt es alle (KPHX→KLAS, KDCA→KJFK, LIRF→LFMN, SBRJ→SBFI). Die Ankerplätze EGPE, EICK, EGNS, FSIA, LSGG, LSZH, LOWI, EGLL und TNCM auch.
- **Abdeckung zählt nur echte Ankünfte** (`build_v2.py:509-511`), keine Ausweichplätze. Ein geschlossener Datensatz bricht den Build ab (`:513`). VHHX ist ausgeschlossen und im Test abgedeckt.
- **UKLL:** Laut EASA-Seite gilt CZIB-2022-01R14 (Revision 24.07.2026) bis 31.01.2027. FIR Lviv ist per NOTAM A0021/26 für zivile Flüge geschlossen. Die Formulierung „nur Simulator-Ausnahme“ ist also richtig.
- **Keine versehentliche A320-Freigabe:** Neue A320-Vorschläge gibt es nur für KSAN, KLGA, LIPZ, LIMJ und SBSP, alles reguläre A320-Plätze. Für LCY, Saba, Barra, Praslin, Courchevel und Samedan wird keiner vorgeschlagen. EGLC bekommt keine Twin Otter.
- **XSS/Validierung:** `esc()` maskiert auch `"` und `'`. Alle neuen Links laufen durch `esc` und sind beim Build auf `https` ohne Zugangsdaten beschränkt (`is_url`, `:197-204`). Einen Weg für `javascript:`-Links habe ich nicht gefunden.
- **Linkkorrekturen:** `PRODUCT_LINK_CORRECTIONS` (`integrate_research.py:246-254`) ersetzt nur den exakt bekannten alten Link. Neue Produkte werden nicht pauschal überschrieben.
- **Runner:** In `run_opus.py:17,25,27` ist `--effort` sauber umgesetzt und wird auch in der Meta-Datei protokolliert.

## Befunde

**P2-1 · `build_v2.py:519-523` – Jeder enthaltene Audit-Airport wird zum Top-Highlight**
- `airports[ident]["level"] = 2` wird ohne Bedingung gesetzt und überschreibt die redaktionelle Stufe aus `content.json`.
- Betroffen sind Airports mit Stufe 1: KLAS, KSFO, YSSY, VHHH, LFMN, ENTC, FSIA. Dazu kommen Airports ohne Stufe: EGLL, KBOS, SCEL, NFFN, RJTT, OMDB, HRYR, vermutlich auch NTTB.
- Folge: Rund 15 zusätzliche Highlight-Karten und `hl2`-Kartenmarker. Die Texte sind teils dünn, etwa „Nadi – Fidschi.“ oder „Tokio-Haneda – handgefertigt im Basis-Sim.“. Die Tags sind die Namen aus dem Audit, z. B. „London Heathrow“.
- Damit wird eine Forums- oder Umfrage-Erwähnung automatisch zur redaktionellen Hervorhebung.
- Der Test (`check_links_highlights.py:28`) prüft nur TFFJ.
- **Empfehlung:** Die Stufe nur über ein ausdrückliches Feld (z. B. `"promote": true`) setzen oder direkt in `content.json` pflegen. Für St. Barth reicht ein Eintrag in `content.json`.

**P2-2 · `highlight-audit.json:318` – EGLC ist zu weich formuliert**
- Hubschrauber sind in London City laut Baugenehmigung verboten, ausgenommen Rettung, Polizei und SAR. Auch der A320 ist dort nicht zugelassen.
- „Nicht pauschal als zulässig behandeln … gesondert klären“ klingt nach einer offenen Frage. Tatsächlich ist die Antwort klar: Keiner der beiden bevorzugten Typen darf landen.
- **Empfehlung:** Das eindeutig so formulieren. Als Alternative einen H160-Flug entlang der Themse-Hubschrauberroute mit Blick auf die Docklands anbieten, Landung an einem aktiven Heliport wie EGLW Battersea. Die Einstufung „Hohe Priorität“ überdenken.

**P2-3 · `build_v2.py:350-353` und `app.js:1048` – Neue A320-Legs würden die Fortschritts-IDs verschieben**
- Die IDs `L###` werden fortlaufend nummeriert. Wer KSAN, KLGA, LIPZ, LIMJ oder SBSP einfügt, verschiebt alle folgenden IDs. Betroffen wären der gespeicherte Fortschritt, das Debriefing-Archiv (der Build würde laut abbrechen) und der V1-Import.
- KSAN und KLGA ersetzen außerdem bestehende Legs.
- Für den eingefrorenen Stand ist das kein Fehler, weil nichts übernommen wird. Der Satz „Fortschritts-IDs bleiben erhalten“ gilt aber nur, solange es so bleibt.
- **Empfehlung:** Bei den A320-Vorschlägen vermerken, dass eine Übernahme eine ID-Migration oder stabile IDs braucht. H160-Ausflüge (`X-…`) sind davon nicht betroffen.

**P3-1 · `app.js:1137` mit `:1354` – Klicks im aufgeklappten Bereich öffnen das Briefing**
- Die Zeilen `<tr data-go>` in der Tabelle „Angebot recherchiert“ enthalten jetzt das aufklappbare `details.scenery-references`.
- Ein Klick auf den Kontexttext, den Hinweis oder die Leerfläche springt zum Briefing. Die Ausnahme greift nur für `a` und `summary`.
- **Empfehlung:** `t.closest('a, summary, .scenery-references')`. Der UI-Test deckt diesen Fall nicht ab.

**P3-2 · `highlight-audit.json:304-307` – Saba: Beleg passt nicht zur Aussage**
- „Hubschrauberverkehr ist belegt“ stützt sich nur auf die Anreiseseite von Saba Tourism. Die war für mich nicht abrufbar (503) und beschreibt vermutlich Winair und Fähre.
- Hubschrauber-Charter gibt es tatsächlich, etwa West Indies Helicopters ab Grand Case und St. Maarten.
- **Empfehlung:** Eine Quelle eines Hubschrauberbetreibers als `activeSources` ergänzen.

**P3-3 · `highlight-audit.json:147-155` – VHHH ist möglicherweise falsch zugeordnet**
- Die FR24-Erwähnung „sweeping turn over Hong Kong“ meint sehr wahrscheinlich die Kai-Tak-Kurve.
- Die Kennzeichnung „kein Kai Tak“ ist richtig. Als Beleg für VHHH trägt diese Quelle aber wenig.

**P3-4 · `build_v2.py:520` – `highlightSources` wird nie angezeigt**
- Das Feld wird geschrieben, aber `app.js` liest es nirgends. Entweder anzeigen oder weglassen.

**P3-5 · Kleinere Validierungslücken**
- Doppelte URLs in `scenery-links` fängt nur der Test ab, nicht der Build.
- Unbekannte Felder in `scenery-links` und in Audit-Einträgen werden nicht geprüft.
- Fehlt `highlight_audit["airports"]`, gibt es einen `KeyError` statt einer klaren Meldung.
- Die Linkkorrekturen passen nur auf exakt gleiche URLs. Eine leicht abweichende Such-URL (z. B. mit Schrägstrich am Ende) würde ohne Warnung durchrutschen.

**P3-6 · Bestehende Tour, nicht neu (`coverage: "A320"`)**
- MHTG steht als „A320 · L…“ in der Tabelle. Große Jets wurden 2021 nach Palmerola verlegt. Die Beschriftung sollte nicht als Nachweis für realen A320-Betrieb gelesen werden, die Sonderetappe ist ja entsprechend markiert.

## Fachliche Einschätzung der Vorschläge

- **In Ordnung:**
  - KSAN: Beide Teilstrecken bleiben unter zwei Stunden.
  - LIPZ oder LIMJ: sinnvoll als Entweder-oder.
  - SBSP: A320 auf kurzer Bahn, Performance-Prüfung ist genannt.
  - FSPP und LFLJ: kurze H160-Ausflüge, bei Courchevel mit Belegen für Hubschrauberbetrieb.
  - LSZS: mit Hubschrauber-Beleg.
  - KLGA: Die Überlegung, KDCA→KJFK umzuplanen statt eines 10-NM-Hüpfers zu JFK, ist richtig.
- **Barra:** Die Twin Otter als freiwillige Ausnahme ist nachvollziehbar begründet. Gegen die Nutzervorgabe verstößt das nicht, die galt nur für EGLC.
- **EIDL:** Die H160-Strecke ab EICK ist mit etwa 190 NM lang. Ab EGNS sind es etwa 145 NM. Ob es einen näheren Ankerplatz gibt, habe ich nicht geprüft.
- **Mögliche weitere Kandidaten, nicht geprüft:** Gisborne NZGS (Bahnstrecke kreuzt die Piste), Sumburgh EGPB, Juneau PAJN, Sion LSGS. Sie fehlen in der Tour und im Audit. Aufnehmen sollte man sie erst nach einer eigenen Betriebsprüfung.

## Grenzen

- Nur gelesen, keinen Build und keine Tests selbst ausgeführt. Die PASS-Ergebnisse stammen von Astra.
- Keine Browserprüfung.
- Ob die Seiten der Nachweis-Links aktuell wirklich laufenden Betrieb belegen, habe ich nur stichprobenartig geprüft. Saba Tourism (503), LCY-Operator-Seite (403) und FR24 (403) konnte ich nicht direkt abrufen, FR24 nur über die Websuche bestätigt.
- `scenery-links.json` habe ich inhaltlich nicht bewertet, wie vorgegeben, nur Schema und Darstellung.
- Das Audit ist eine qualitative Auswahl, kein Ranking.
- Leistung von H160 und A320 im Simulator ist nicht getestet.

Quellen:
- [EASA CZIB-2022-01R14](https://www.easa.europa.eu/en/domains/air-operations/czibs/czib-2022-01r14)
- [IVAO – London City EGLC](https://wiki.ivao.aero/en/home/divisions/xu/atc/aerodrome/local-procedure/london/eglc)
- [Simple Flying – LCY approved aircraft](https://simpleflying.com/london-city-airport-approved-aircraft/)
- [UK CAA – London helicopter operations](https://www.caa.co.uk/data-and-analysis/airspace-and-environment/airspace/london-helicopter-operations/)
- [West Indies Helicopters – Sint Maarten → Saba](https://www.westindieshelico.com/sint-maarten-to-saba-island-helicopters/)
- [FR24 Blog – scenic approaches thread](https://www.flightradar24.com/blog/threads/which-airport-approach-or-departure-do-you-think-is-the-most-scenic/)