# Linkprüfung und Ergänzung – Opus 5.5, Medium Effort

Projekt M:/flightsim/VolantaWorldTour. Nutzer möchte fehlende Links in Freeware/Payware-Vorschlägen korrigiert sowie aktive Luftfahrt-Highlights abgeglichen haben. Astra recherchiert Highlights und implementiert Darstellung/Build. Du übernimmst unabhängig die Linkdaten. Keine Unteragenten, keine Shell, keine Commits/Publikation. Nutzer hat für DIESEN Auftrag ausdrücklich medium statt max gewählt.

Lies v2/content.json, v2/research-2026-09-24.json und ggf. work-Recherche. Alle 170 strukturierten scenery-Einträge besitzen bereits url! Die wahrscheinlich fehlenden Links sind namentlich erwähnte Produkte/Alternativen in defaultOk, why, ownedNotes, airport briefs, dependencies und installNote. Prüfe systematisch sämtliche relevanten Texte und bestehenden strukturierten Verweise. Bestehende recherchierte URLs nutzen; fehlende mit WebSearch/WebFetch auf Produkt-/Herstellerseiten/flightsim.to/FSAddonCompare auflösen. Keine geratenen URLs; Suchresultatlinks als solche kennzeichnen, besser konkrete Produktseiten. Kein Kaufstatus nur wegen neuem Link; Qualitätsvorbehalte erhalten. Keine Behauptung, alle URLs live getestet zu haben, wenn nicht erfolgt.

Du darfst NUR folgende Dateien schreiben:
- v2/scenery-links.json (neu): Objekt ICAO -> Array von {"label": "Produkt · Entwickler", "url": "https://...", "context": "Erwähnte Alternative; keine neue Empfehlung"}. Nur ergänzende Quellen/Produktlinks, die in der bisherigen Oberfläche nicht verlinkt sind. Bereits als scenery.url/alt/dependency bei diesem Airport sichtbare identische Links nicht duplizieren. Auch Quellen für produktbezogene defaultOk-Texte ergänzen. Astra rendert dieses Objekt auf Flughafenkarten und im Szenerienbereich und validiert https URLs.
- v2/content.json: ausschließlich belegte Linkkorrekturen oder fehlende alt/dependency URLs, keine Highlights oder Routenänderungen, keine Qualitäts-Upgrades. Falls Text ein identifizierbares Produkt bloß unklar erwähnt, darfst du dessen Namen präzisieren.
- v2/collaboration/2026-09-25-links-highlights/opus-links-result.md: vollständiger Bericht mit Umfang, Datenfehlern, überprüften Quellen, verbleibenden ungeklärten Verweisen und statischer Prüfung.

Quellenarchiv kann sehr groß sein: fokussiert lesen. Wenn 403 ausgegebene Airports vs 385 Inhalts-Airports, berücksichtige tatsächlich verwendete tour-v2.json Airports. Nimm alle fehlenden eindeutig identifizierbaren Angebote auf, auch wenn verworfen; context muss Ablehnung/Kandidatenstatus unmissverständlich nennen. Quellenverweise dürfen eine Auswahl verlinken, ohne eine Empfehlung vorzutäuschen.

Abschluss: überprüfe eigene neue JSON syntaktisch durch sorgfältiges Lesen; Tests führt Astra aus. Liefere präzise Zahlen. Danach erfolgt gegenseitige Review.
