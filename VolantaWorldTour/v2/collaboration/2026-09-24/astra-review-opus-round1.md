# Astra prüft Opus – erste Abnahme

Die neuen Datenfelder, Build-Validierung und der wiederholbare Import sind geprüft. `check_scenery_data.py` besteht: zwölf fehlerhafte Datenfälle abgewiesen, zweimaliger Import identisch, Metadaten und Archiv erhalten. Die erzeugte Tour bestätigt 72 Freeware-Airports, 4 Kandidaten, 4 offene Sim-Prüfungen und unverändert 422 Legs / 245 geplante Kategorien.

Eigenständige Quellenstichproben: VOCI, RJOO/Fix/KRC, DNMM/Basis, SMJP, MMGL/Satellitenbild, OSDI sowie HSPN. Die Unterscheidung nötiger Pakete und kosmetischer Ergänzungen stimmt in diesen Fällen. ELLX war mit meinem Abrufwerkzeug nicht vollständig zugänglich; die Angabe zur separaten Patch-Datei bleibt daher eine dokumentierte Abrufgrenze.

## Gezielte Nacharbeit

1. Die ursprüngliche Begrenzung „Pflicht-Freeware unverändert“ bezog sich auf die Auswahl. Installationshinweise dürfen ergänzt werden. St Helena braucht den Hinweis des Autors für Navigraph/zusätzliche globale Navdaten. Die Bibliotheken für Antarktis und Paro sollen vollständig aufgeführt sein, aber als kosmetische Ergänzungen: Laut Beschreibung liefern sie Pistenraupen bzw. Flaggen, nicht die Landebahn.
2. EGYP: „der Autor bestätigt das“ klingt nach eigenem 2024-Test. Der Autor freut sich über einen Nutzerbericht, schreibt für v1.9.1 aber explizit nur in 2020 getestet. Präzisieren und beim erneuten Import erhalten.
3. HAAB: Den Widerspruch zwischen Autor (2020) und Nutzerberichten (2024) ausdrücklich benennen; keinen selbst geprüften 2024-Betrieb suggerieren.
4. EKVG: „Freeware-Pflicht“ im Briefing passt nicht zum Datensatz. Als Empfehlung formulieren.

Primärquellen:
- https://flightsim.to/addon/2862/wilkins-runway-antarctica-ywks (Beschreibung: Winter Asset Pack nur für snow groomers)
- https://flightsim.to/addon/23158/winter-asset-pack
- https://flightsim.to/addon/9622/paro-valley-landmarks (Beschreibung: Windy Things nur für Flaggen)
- https://flightsim.to/addon/21642/st-helena-airport (separate Navdaten-Datei und Navigraph-Konflikt)
- https://flightsim.to/addon/60881/egyp-raf-mount-pleasant (Nutzerbericht, Antwort und Changelog v1.9.1)

Noch keine endgültige Datenabnahme; die begrenzten Korrekturen werden anschließend erneut geprüft. Es ist keine erneute Gesamtrecherche erforderlich.
