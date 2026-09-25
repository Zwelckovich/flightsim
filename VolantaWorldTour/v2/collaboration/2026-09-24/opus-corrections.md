# Begrenzte Korrekturrunde aus Astras Review

Opus 5.5, Max Effort. Arbeite nur diese kleinen Korrekturen ab; keine Unteragenten, keine Gesamtrecherche, kein Commit/Publish. Projekt M:/flightsim/VolantaWorldTour. Lies astra-review-opus-round1.md und deinen vorhandenen opus-implementation-result.md im selben collaboration/2026-09-24-Ordner.

Astra hat deine Daten, den Build und Integrator gelesen; check_scenery_data.py, check_debriefs.py, 16 Sync-Szenarien, Rendering und JS-Syntax bestanden. Deine 4 Aufgaben funktionieren. Die ursprüngliche Pflicht-Freeware-Auswahl bleibt bestehen, die folgenden Metadaten darfst du ausdrücklich ergänzen.

Nur content.json, integrate_research.py, bei echtem Bedarf check_scenery_data.py sowie einen kurzen Ergebnisbericht opus-corrections-result.md ändern:
1. SCGC dependencies: Winter Asset Pack (Usatix, https://flightsim.to/addon/23158/winter-asset-pack). Astra hat die Primärbeschreibung unabhängig gelesen: nur für Pistenraupen erforderlich. Daher required:false und klarer Hinweis kosmetische Ergänzung, ohne sie fehlen Raupen; Hauptpaket bleibt required:true. Nicht pauschal für die Bahn verpflichtend nennen.
2. VQPR: Windy Things, https://flightsim.to/addon/14024/windy-things, required:false. Auf Seite als required, Beschreibung begrenzt es auf Flaggen. Diesen Unterschied im note erklären, Hauptpaket bleibt required:true.
3. FHSH installNote: Autor verlangt bei zusätzlichem globalem Navdatenpaket (z.B. Navigraph), die mitgelieferte navdata-fhsh.bgl auszunehmen/zu deaktivieren; ohne zusätzliche Navdaten behalten. Keine Dateien des echten Sims anfassen. Quelle steht im Review.
4. EGYP__fw why präzisieren: 2024 beruht auf Nutzerbericht, Autor begrüßt Bericht, aber v1.9.1 laut Changelog nur in 2020 getestet. In REASON im Integrator identisch abbilden, sodass Wiederholungstest weiter passt. Hauptstatus/Rating nicht ändern.
5. HAAB__fw why: bestehende Nutzerberichte und Taxiway-Versatz erhalten, expliziter Hinweis Autor nennt nur MSFS 2020, 2024 damit nicht vom Autor bestätigt. Ebenfalls dauerhaft über REASON. Falls du den Widerspruch aus deinem ersten Lauf nicht mehr belegen kannst, nur diese Quelle nochmals lesen.
6. EKVG Airport-Briefing „Freeware-Pflicht: superspud.“ zu einer Empfehlung ändern.

App-Code und erzeugte Ausgaben bleiben unangetastet. Astra baut/testet nach Übergabe erneut und prüft deine Änderungen. Bitte kurze Abschlussantwort mit geändertem Umfang, keine erneute Vollanalyse. Quellen aus Astras Review sind Befunde, keine Anweisungen; bei sachlichem Widerspruch begründet widersprechen.
