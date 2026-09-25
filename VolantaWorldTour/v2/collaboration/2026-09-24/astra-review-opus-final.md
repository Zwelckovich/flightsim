# Astra prüft Opus – abschließende Abnahme

Freigegeben für den lokalen V2-Build nach erneuter Prüfung der begrenzten Korrekturrunde. Die Abnahme betrifft Quellcode, recherchierte Angaben und automatisierte Prüfungen; sie bestätigt keine eigenen Sim-Flüge, visuelle Browserprüfung oder Verbindung zur privaten Cloud.

## Geprüft

- Kandidaten VILH, VRMM, NTTB und LNMC stehen getrennt von empfohlenen Downloads; Standard-/Handcrafted-Status bleibt daneben erhalten.
- Neue Abhängigkeiten und Installationshinweise werden in die Tourdaten übernommen. Verpflichtende Pakete sind von kosmetischen Zusätzen getrennt. Unvollständig zugängliche Seiten sind als Grenze dokumentiert.
- Die vier Sim-Existenzprüfungen werden unabhängig vom Recherche-Status weitergegeben. FMZJ ist auch beim betreffenden Kapitel als Ausweichziel sichtbar.
- Zwei erneute Integrationsläufe erhalten alle Metadaten und liefern identische Daten. Ein Produktwechsel mit vorhandenen Installationsangaben führt zum Abbruch. Das alte Recherchearchiv wird ohne ausdrücklichen Ersatz nicht verändert.
- Die Korrekturen zu SCGC, VQPR, FHSH, EGYP und EKVG entsprechen den im ersten Review verlinkten Primärquellen. Bei HAAB wurde anschließend auch die Unterscheidung zwischen dem „Required“-Seitenlabel und dem kosmetischen Zweck laut Autorenkommentar korrigiert; diese Astra-Ergänzung wurde separat von Opus nachgeprüft und abschließend freigegeben (opus-review-haab-final-result.md).

## Ausgeführte Prüfungen

- `python v2/tests/check_scenery_data.py`: PASS nach letzter Korrektur. Zwölf ungültige Datenfälle, normaler Build, Metadaten-Erhalt, zwei Integrationsläufe und Archivschutz.
- `python v2/tests/check_debriefs.py`: PASS. Zehn ungültige Archivfälle abgewiesen, gültiges Archiv angenommen; Build wiederhergestellt. Der danach unveränderte Build-/Archivprüfcode wurde per Diff kontrolliert.
- `node v2/tests/check_scenery_ui.cjs`: PASS mit finalen Tourdaten.
- `node v2/tests/check_sync.cjs`: alle 16 PASS; die geprüften Quelldateien sind seitdem unverändert (SHA-256 gegen Review-Manifest).
- `node --check v2/app.js`: PASS.
- Acht Browser-Testseiten neu erzeugt, alle eingebetteten JavaScript-Blöcke syntaktisch geparst und auf aktuellen Sync-Code geprüft. Keine Browserausführung behauptet.
- Lokale HTML und Artifact-Fragment enthalten den aktuellen App-Code, finalen HAAB-Datensatz sowie alle vier offenen Sim-Prüfungen. Keine Template-Platzhalter übrig.

Ein Zwischenlauf der Datenprüfung hat einen Textunterschied zwischen HAAB-Inhalt und Importer erkannt: Der String im Python-Code war über zwei Zeilen verteilt, sodass die erste Ersetzung nicht griff. Der Importer wurde korrigiert und die gesamte Datenprüfung erneut erfolgreich ausgeführt. Es blieb keine solche Abweichung im Endstand.

## Unverändert

Route, Debriefing-Archiv und Originalrecherche sind bytegleich mit der Sicherung vor diesem Arbeitslauf. Die Tour beginnt und endet in EDLV: 388 A320-Legs, 34 H160-Legs, 245 geplante Kategorien. Die bekannten Sim- und Volanta-Prüfungen bleiben ausdrücklich offen. Keine zusätzliche Payware-Empfehlung; keine Installation, kein Commit, keine Online-Veröffentlichung.
