# Unser Debriefing nach jedem Leg

Nach dem Flug erzählst du hier im Chat kurz, welches Leg du geflogen bist und welche Airport-Szenerien tatsächlich aktiv waren. Ich ordne den Bericht dem Leg zu, dokumentiere deine Angaben in `debriefings.json` und baue die HTML neu. Du musst keine JSON-Datei selbst bearbeiten.

Hilfreich sind:

- Flugdatum und tatsächlich verwendetes Flugzeug.
- Abflug- und Ankunfts-Airport: Hersteller, Produkt, wenn bekannt Version. Auch MSFS-Standard oder ein World-Update-Airport wird ausdrücklich als tatsächlich verwendet erfasst.
- Zusätzliche Landschafts- oder Stadt-Add-ons; bei bewusst keinen zusätzlichen Add-ons „keine“ nennen.
- Tatsächlicher Anflug, Bahn/Landeplatz, Wetter und Tageszeit.
- Persönliches Highlight, Performance, Probleme und Szenerie-Fazit.
- Was beim nächsten Flug anders oder besser sein sollte; Volanta-Gutschrift nach dem Flug, sofern kontrolliert.

Du kannst frei erzählen. In der HTML gibt es pro Leg auch eine kopierbare Gesprächsvorlage. Ist etwas unklar, bleibt es offen. Empfehlungen, Installationsbestand und tatsächliche Nutzung sind getrennte Fakten. Ein fehlender Problembericht bedeutet nicht automatisch „keine Probleme“.

## Dauerhafte Dokumentation

`debriefings.json` ist die maßgebliche Datei im Git-Projekt. Jeder Bericht verweist über `legId`, `from` und `to` eindeutig auf ein Leg; die laufende Flugnummer der Gesamtroute ist keine Leg-ID. A320-IDs sind Zeichenketten wie `"1"`, Ausflugs-IDs beispielsweise `"X-GG-1"`. Für die exakte ID die HTML-Vorlage oder die Routendaten verwenden.

`draft` bedeutet, dass Angaben zur tatsächlichen Nutzung noch offen sind. `final` setzen wir erst, wenn die tatsächlich verwendeten Szenerien an Abflug und Ankunft aus deinem Bericht bekannt sind. Andere nicht genannte Angaben, etwa Versionsnummer oder Wetter, bleiben auch im Finalbericht als „Noch nicht angegeben“ sichtbar. Die Volanta-Wertung bleibt ohne deinen Nachweis offen.

Die HTML zeigt alle Berichte im Bereich **Debriefing** und bietet direkte Verknüpfungen aus den Leg-Briefings und der gesamten Flugreihenfolge. Der Build erzeugt außerdem `outputs/Debriefings.md` als lesbares Tourtagebuch. Beide Ausgaben werden aus der JSON-Datei erstellt; nicht von Hand bearbeiten.

Flug-Häkchen bleiben davon unabhängig im Browserspeicher. Sie kennzeichnen offene Debriefings, erzeugen aber keinen Bericht. Das Entfernen eines Häkchens löscht keinen Bericht. Der Fortschritts-Export enthält weiterhin nur Häkchen; der separate Debriefing-Export und die Projektdateien enthalten das Archiv. Für Browserwechsel oder Dateiverschiebungen den Fortschritt separat exportieren/importieren. Im Projekt gespeicherte Berichte reisen bereits mit der HTML mit.

Einträge lassen sich bei späteren Korrekturen aktualisieren. Git kann Änderungen nachverfolgen, sobald du sie committest; der Build erstellt selbst keine Commits. Eine einzelne gute oder schlechte Erfahrung ändert keine generelle Kaufempfehlung automatisch. Wenn dein Bericht eine Empfehlung infrage stellt, halten wir das im Fazit fest und überprüfen die Empfehlung gezielt.

## Eintrag pflegen

Vor jedem Eintrag die aktuelle Route und vorhandene Berichte lesen. Bestehende Fakten erhalten, nur berichtete Tatsachen ergänzen. Keine geplante Szenerie als tatsächlich verwendet kopieren. Bei einem abweichend geflogenen Abflug oder Ziel erst die Abweichung klären; nicht die geplanten Endpunkte als geflogen ausgeben. `updatedAt` ist das tatsächliche Bearbeitungsdatum, `flightDate` nur das berichtete Flugdatum (sonst `null`). Unbekanntes wird mit `null` gespeichert; „keine“ oder „keine Probleme“ sind ausdrückliche Nutzeraussagen.

Die folgende Struktur ist eine **Vorlage, kein geflogenes Leg**. `legId`, `from` und `to` aus der Route einsetzen; das Datum ersetzen. Die Platzhalter werden vom Build absichtlich nicht akzeptiert.

```json
{
  "legId": "<feste Leg-ID>",
  "from": "<ICAO Abflug>",
  "to": "<ICAO Ankunft>",
  "status": "draft",
  "updatedAt": "YYYY-MM-DD",
  "flightDate": null,
  "aircraft": null,
  "actualScenery": {
    "departure": {"product": null, "version": null},
    "arrival": {"product": null, "version": null},
    "landscape": null
  },
  "approach": null,
  "conditions": null,
  "highlights": null,
  "issues": null,
  "verdict": null,
  "nextTime": null,
  "volanta": "open"
}
```

`volanta` erlaubt `open`, `credited` und `not_credited`. Ein Bericht pro Leg; Korrekturen im bestehenden Eintrag. Bei wiederholten Flügen vor dem Überschreiben besprechen, welche Durchführung das Tour-Leg dokumentiert.

Nach dem Aktualisieren `Build-Worldtour.ps1` ausführen. Der Build prüft Leg-ID, Strecke, doppelte Einträge, Status, Datumsfelder und die beiden tatsächlichen Airport-Szenerien bei Finalberichten. Dann die Änderung anhand der HTML und des erzeugten Tagebuchs prüfen. Bestehende Empfehlungen und Routendaten nur bei einer ausdrücklich besprochenen Änderung anfassen.


## Zurücksetzen

Unter **Planung & Quellen → Tour zurücksetzen** gibt es zwei getrennte Buttons mit Bestätigungsdialog:

- **Flugfortschritt zurücksetzen:** entfernt alle A320-, Ausflugs- und archivierten Flug-Häkchen aus diesem Browser. Die Debriefings bleiben erhalten. Eine JSON-Sicherung kann vor dem Reset heruntergeladen und über „Sicherung laden“ wiederhergestellt werden. Ein blockierter Browserspeicher verhindert den Reset.
- **Debriefings im Projekt leeren:** entfernt alle aktiven Berichte aus `debriefings.json`, den beiden HTML-Ausgaben und `outputs/Debriefings.md`. Die Flug-Häkchen bleiben erhalten. Der Button ist auch direkt im Debriefing-Bereich verfügbar.

Für einen vollständigen Neustart beide Optionen verwenden. Die Tourroute, Empfehlungen und das Volanta-Konto werden nicht geändert. Bereits bestehende Sicherungen oder Git-Commits werden ebenfalls nicht gelöscht.

Der Debriefing-Reset benötigt schreibenden Ordnerzugriff im Browser, beispielsweise in Microsoft Edge oder Google Chrome. Nach der Bestätigung den Projektordner `VolantaWorldTour` auswählen (mit `debriefings.json` und `work`, nicht den übergeordneten Git-Ordner). Die HTML prüft, dass die Dateien zur geöffneten Tour und zum angezeigten Archivstand passen. Bei Abweichungen zunächst `Build-Worldtour.ps1` ausführen und die HTML neu öffnen.

Vor dem Leeren werden alle vier betroffenen Dateien vollständig unter `backups/debrief-reset-…/` gesichert. Ohne erfolgreiche Sicherung wird nichts geleert. Bei Schreibfehlern versucht der Reset, bereits begonnene Änderungen aus den Originalen zurückzunehmen; im Fehlerdialog steht der Sicherungspfad. Bei Browserabbruch oder fehlgeschlagener Wiederherstellung die betroffenen Dateien aus dieser Sicherung zurückkopieren. Während des Resets das Fenster geöffnet lassen und das Projekt nicht parallel bearbeiten.

Nach erfolgreichem Reset sind die Projektdateien und die aktuelle Ansicht aktualisiert; ein anschließender Neubau übernimmt das leere Archiv. Andere bereits geöffnete HTML-Tabs neu laden. Um Berichte später wiederherzustellen, `debriefings.json` aus dem gewünschten Sicherungsordner zurückkopieren und `Build-Worldtour.ps1` ausführen. Die Berichte sind im Sicherungsordner weiterhin enthalten; der Reset ist keine Löschung sämtlicher historischer Kopien.

Technische Referenz für den Browserzugriff: [Chrome – File System Access API](https://developer.chrome.com/docs/capabilities/web-apis/file-system-access).
