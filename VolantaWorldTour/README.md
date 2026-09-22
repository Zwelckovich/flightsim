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

## Debriefing nach jedem Leg

Nach einem Flug besprechen wir hier im Chat die tatsächlich verwendeten Airport- und Landschafts-Szenerien, Anflug-Highlights, Performance und Probleme. Der Bereich **Debriefing** in der HTML zeigt offene und final dokumentierte Legs und bietet Gesprächsvorlagen für alle 449 Legs.

Die dauerhaften Berichte liegen in `debriefings.json` und werden in die HTML eingebettet. Zusätzlich entsteht beim Build `outputs/Debriefings.md` als lesbares Tourtagebuch. Der genaue Ablauf und das Datenformat stehen in `DEBRIEFING.md`. Empfehlungen werden niemals automatisch zu verwendeten Produkten; bisher wurden noch keine Flüge debrieft.

Flug-Häkchen im Browser und Berichte im Projekt sind getrennt. Fortschritts-Backups sichern weiterhin die Häkchen; Debriefings lassen sich separat als JSON exportieren und sind bereits Teil der Projektdateien. Der Build prüft die Zuordnung jedes Berichts zu Leg und Strecke. Die Build-Pfade sind relativ zum Projekt, auch nach dem Umzug nach `M:\flightsim\VolantaWorldTour`.


## Zurücksetzen

Unter **Planung & Quellen → Tour zurücksetzen** gibt es zwei getrennte Buttons mit Bestätigungsdialog:

- **Flugfortschritt zurücksetzen:** entfernt alle A320-, Ausflugs- und archivierten Flug-Häkchen aus diesem Browser. Die Debriefings bleiben erhalten. Eine JSON-Sicherung kann vor dem Reset heruntergeladen und über „Sicherung laden“ wiederhergestellt werden. Ein blockierter Browserspeicher verhindert den Reset.
- **Debriefings im Projekt leeren:** entfernt alle aktiven Berichte aus `debriefings.json`, den beiden HTML-Ausgaben und `outputs/Debriefings.md`. Die Flug-Häkchen bleiben erhalten. Der Button ist auch direkt im Debriefing-Bereich verfügbar.

Für einen vollständigen Neustart beide Optionen verwenden. Die Tourroute, Empfehlungen und das Volanta-Konto werden nicht geändert. Bereits bestehende Sicherungen oder Git-Commits werden ebenfalls nicht gelöscht.

Der Debriefing-Reset benötigt schreibenden Ordnerzugriff im Browser, beispielsweise in Microsoft Edge oder Google Chrome. Nach der Bestätigung den Projektordner `VolantaWorldTour` auswählen (mit `debriefings.json` und `work`, nicht den übergeordneten Git-Ordner). Die HTML prüft, dass die Dateien zur geöffneten Tour und zum angezeigten Archivstand passen. Bei Abweichungen zunächst `Build-Worldtour.ps1` ausführen und die HTML neu öffnen.

Vor dem Leeren werden alle vier betroffenen Dateien vollständig unter `backups/debrief-reset-…/` gesichert. Ohne erfolgreiche Sicherung wird nichts geleert. Bei Schreibfehlern versucht der Reset, bereits begonnene Änderungen aus den Originalen zurückzunehmen; im Fehlerdialog steht der Sicherungspfad. Bei Browserabbruch oder fehlgeschlagener Wiederherstellung die betroffenen Dateien aus dieser Sicherung zurückkopieren. Während des Resets das Fenster geöffnet lassen und das Projekt nicht parallel bearbeiten.

Nach erfolgreichem Reset sind die Projektdateien und die aktuelle Ansicht aktualisiert; ein anschließender Neubau übernimmt das leere Archiv. Andere bereits geöffnete HTML-Tabs neu laden. Um Berichte später wiederherzustellen, `debriefings.json` aus dem gewünschten Sicherungsordner zurückkopieren und `Build-Worldtour.ps1` ausführen. Die Berichte sind im Sicherungsordner weiterhin enthalten; der Reset ist keine Löschung sämtlicher historischer Kopien.

Technische Referenz für den Browserzugriff: [Chrome – File System Access API](https://developer.chrome.com/docs/capabilities/web-apis/file-system-access).
