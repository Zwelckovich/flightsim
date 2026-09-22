# Volanta Worldtour ab EDLV

Öffne **Volanta-Worldtour-EDLV.html** direkt im Projektordner mit deinem Browser. Die HTML enthält Karte, Daten und Programmcode vollständig; ein Webserver ist nicht erforderlich. Externe Recherchelinks benötigen Internet.

## Projektinhalt

- `Volanta-Worldtour-EDLV.html`: direkt zugängliche Startdatei.
- `outputs/Volanta-Worldtour-EDLV.html`: identische Ausgabe des HTML-Generators.
- `work/`: vollständige Quelldaten, HTML/CSS/JavaScript-Vorlagen, Python-Skripte, Prüfungen und gespeicherte Rechercheergebnisse.
- `MSFS Airports - Addons.csv`: deine bereits vorhandene Airport-Sammlung.
- `Build-Worldtour.ps1`: erstellt die HTML aus den aktuellen Quelldaten und führt die vorhandenen Prüfungen aus.

Stand: 21.09.2026. Die Planung umfasst 449 zusammenhängende Legs, 405 Landestellen und 245 Volanta-Kategorien. Hauptflugzeug ist der Fenix A320; 18 Ausflüge verwenden den H160, nur der Antarktis-Ausflug die Twin Otter. Die Hinweise zu Reichweite, Tankstopps, Sonderbetrieb und offenen Szenerieprüfungen stehen in der HTML.

## Neu erstellen

Voraussetzungen: Python 3 und Node.js im Suchpfad. Für diesen Build sind keine zusätzlichen Pakete und keine neuen Downloads erforderlich.

Im Projektordner ausführen:

```powershell
.\Build-Worldtour.ps1
```

Nach Änderungen an Szenerie-Empfehlungen auch die abgeleiteten Szeneriedaten erneuern:

```powershell
.\Build-Worldtour.ps1 -RebuildScenery
```

Maßgebliche Daten: `work/tour-data.json`, `work/excursions.json`, `work/briefings.json`, `work/freeware-research.json` und `work/maker-review.json`. Der aktuelle Build-Ablauf ist im PowerShell-Skript festgelegt. Weitere Skripte in `work/` dokumentieren frühere Recherche- und Überarbeitungsschritte; sie sind keine nacheinander auszuführende Build-Pipeline.

## Flugfortschritt

Häkchen werden im lokalen Browserspeicher gespeichert und sind nicht Bestandteil dieser Projektdateien. Vor dem Wechsel von der bisherigen HTML zur Kopie auf Laufwerk M den Fortschritt in der alten HTML als JSON exportieren und in der neuen HTML importieren. Je nach Browser teilen lokale Dateien ihren Speicher oder verwenden getrennte Speicherbereiche.

## Recherchegrenzen

Alle 405 Landestellen sind im Suchabgleich erfasst. 81 haben eine vertiefte Produktprüfung; für 21 Orte gibt es eine gezielte Kaufabwägung. 164 FSAddonCompare-ICAO-Suchen lieferten auswertbare Antworten, 241 blieben ohne auswertbares Ergebnis. Die sechs optionalen Käufe sind Empfehlungen auf Basis der verlinkten Belege, keine eigenen Simulator-Tests. Die HTML hält diese Grenzen pro Airport sichtbar.
