**Nicht freigegeben: Ein Fehler ist noch offen.**

**Inhalt: stimmt.** SniperKP9 fragt, ob ohne die Dependencies Taxiways oder Gates fehlen. Viktoren69 antwortet, sie seien „for esthetics“, also Fahrzeuge, statische Flugzeuge und Container. Taxiways, Jetways und Terminals gehören zur Szenerie. Ohne die Bibliotheken fehle nur „clutter stuff“, der Airport funktioniere für Spieler und KI-Verkehr. In einer Folgeantwort empfiehlt er EDHK für die Beleuchtung des Terminals. In `v2/content.json:3065-3103` ist das richtig umgesetzt: sechs Einträge mit `required: false`, dazu passende Texte in `installNote` und `why`.

**Fehler:** `REASON["HAAB"]` in `v2/integrate_research.py:88-89` enthält noch „sechs Pflicht-Libraries“. Bei einem erneuten Import setzt Zeile 293 `why` neu aus `REASON`. `PRESERVE` in Zeile 244 bewahrt nur `dependencies` und `installNote`. Der korrigierte `why`-Text würde also überschrieben und widerspräche dann `required: false`.

**Korrektur:** In `REASON["HAAB"]` „Pflicht-Libraries“ durch „kosmetische Zusatzbibliotheken“ ersetzen. Das ist der einzige Unterschied zum Text in `content.json`.

Der Befund stammt nur aus dem Lesen der Dateien, ich habe nichts selbst ausgeführt. Astras Lauf mit erneuter Integration hat diese Abweichung offenbar nicht erfasst.

Quelle: https://flightsim.to/addon/60349/haab-addis-abeba-bole