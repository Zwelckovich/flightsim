# Gemeinsamer V2-Arbeitslauf vom 24.09.2026

Autorisierter Test der Zusammenarbeit Codex/Astra + Claude Opus 5.5, fest mit Max Effort. V2 wird weiterentwickelt; keine neue Tourversion. Veröffentlichung und Commit sind nicht Bestandteil dieses Laufs.

## Ablauf und Zuständigkeiten

- Astra: Cloud-Abgleich, Oberfläche, Node-Regressionen und Integrationstests.
- Opus: Szeneriedaten, Installationsangaben, Import und Build-Validierung.
- Opus prüft Astras Code unabhängig; Astra prüft Opus' Änderungen einschließlich eigener Quellenstichproben.
- Jede Seite korrigiert die Befunde; die Gegenseite prüft die Korrekturen nochmals.
- Implementierung und Review arbeiten auf getrennten Dateibereichen. Der Code bleibt während der abschließenden Review-Runde eingefroren.

Der Ausgangsstand wurde vor dem ersten Edit als ZIP mit SHA-256-Manifest unter `C:/Users/zwelc/Documents/Codex/2026-09-21/ich/v2-collaboration-20260924/` gesichert. Die bereits uncommittierten Nutzerdaten wurden nicht zurückgesetzt.

## Austausch und Nachweise

- `opus-implementation.md` / `opus-implementation-result.md`: Arbeitsauftrag und Übergabe der Szeneriearbeit.
- `opus-review-astra-result.md`: erster unabhängiger Review des Sync- und UI-Codes.
- `opus-review-astra-followup-result.md`: Nachprüfung; F1–F4 behoben, Code freigegeben.
- `astra-review-candidate.json`: SHA-256 der fünf eingefrorenen und von Opus geprüften Dateien.
- `astra-review-opus-round1.md` / `opus-corrections.md`: Astras Gegenprüfung und daraus entstandene Nacharbeit.
- `astra-changes.patch`: tatsächliche Änderungen gegenüber dem gesicherten Ausgangsstand (Zeilenenden normalisiert).

Die zentrale Laufsteuerung erfolgte hier in der Codex-Aufgabe: Aufträge, Ergebnisse, Korrekturen und Gegenprüfungen wurden automatisch über lokale Dateien und Claude Code ausgetauscht. Nach der einmaligen Anmeldung war kein Kopieren von Antworten durch den Nutzer erforderlich. Der Runner ist wiederverwendbar:

```powershell
# Vom Projektordner VolantaWorldTour aus; eindeutige Laufnamen verwenden.
python v2/collaboration/run_opus.py <auftragsdatei.md> <laufname>
python v2/collaboration/run_opus.py <reviewauftrag.md> <laufname> --review
```

`--review` erlaubt nur Lesewerkzeuge. Beide Modi erlauben weder Shell-Aufrufe noch Unteragenten; der übergeordnete Agent führt die Tests aus. Der Runner ist ein Baustein für die Koordination, kein unbeaufsichtigt laufender Hintergrunddienst.

## Modell

Claude Code 2.1.235, Aufrufe mit `--model claude-opus-5-5 --effort max`; Provider bestätigt `canonicalModel: claude-opus-5-5`. Es wurde kein Ersatzmodell für Implementierung oder Review gewählt. Transparenz: Claude Codes eingebautes WebFetch verwendet intern laut Nutzungsmetadaten auch Haiku 4.5 zur Zusammenfassung geladener Webseiten. Die Entscheidungen und Reviews stammen von Opus 5.5; Quellenstichproben wurden zusätzlich direkt durch Astra geprüft. Die ausführlichen CLI-Protokolle liegen in ignorierten `.runs/`-Dateien bzw. im ursprünglichen lokalen Arbeitsordner.

## Prüfgrenzen

- Die automatischen Sync-Tests verwenden simulierte Cloud und isolierten Speicher. Die private Artifact-Datenbank wurde nicht verändert und hier nicht live geprüft.
- Der Browserzugriff auf die lokale HTML wurde von der Browser-Sicherheitsprüfung blockiert. Es wurde kein Ausweichweg verwendet; visuelle Abnahme und Ausführung der acht Browser-Testseiten stehen aus.
- Die 16 Node-Sync-Szenarien prüfen Logik; der Renderingtest prüft erzeugtes Markup, kein tatsächliches Layout.
- Für den neuen Cloud-Abgleich müssen alle Geräte die aktualisierte HTML verwenden. Synchronisierung verwendet Gerätezeitstempel und die bereits bekannten Zeitstempel; sie setzt vollständige Collection-Snapshots voraus. Einträge bleiben als Änderungsjournal erhalten; automatische Bereinigung ist nicht implementiert.
- Keine tatsächlichen Flüge oder Add-on-Installationen: Funafuti, Union Glacier und St Helena brauchen weiterhin die dokumentierten Sim-Tests. ZMCK, ZDM, Glorieuses und FMZJ sind ausdrücklich offene Sim-Prüfungen.
- Bei einzelnen Seiten konnte nur der Titel abgerufen werden (insbesondere YPCC, FYWH, FNLU). Der Überblick über benötigte Zusatzpakete ist daher keine Behauptung, sämtliche Downloads selbst installiert zu haben.

## Abschluss

**Abgeschlossen und gegenseitig geprüft.** Opus hat Astras Sync-/UI-Code sowie die letzte HAAB-Korrektur freigegeben. Astra hat Opus' Änderungen und die Korrekturrunde geprüft. Die Hashes der geprüften Dateien stimmen mit dem Endstand überein.

- `astra-review-opus-final.md`: Astras Abnahme einschließlich tatsächlich ausgeführter Tests.
- `opus-review-haab-final-result.md`: letzte Gegenprüfung, freigegeben.
- `validation.json`: Testergebnisse, Prüfgrenzen, Tourstatistik und Hashes der fertigen Dateien.
- `model-runs.json`: sechs abgeschlossene Opus-Läufe mit Modell-/Effort-Nachweis und Ergebnis.

Ergebnis: lokale `Volanta-Worldtour-V2.html` und `v2/dist/artifact.html` neu gebaut. 16 Sync-Szenarien, Szenerie-Datenprüfung und Renderingtest bestanden; zehn ungültige Debriefing-Archive korrekt abgewiesen. Acht Browser-Testseiten erzeugt und auf Syntax geprüft, nicht im Browser ausgeführt. Route und Archivdateien unverändert: 422 Legs, 245 geplante Kategorien. Noch nicht online veröffentlicht oder committiert.

**Lernpunkt für die weitere Zusammenarbeit:** Reviews erst nach bestandenem Testlauf auf eingefrorenen Dateien starten. Der erste HAAB-Review las während einer Textkorrektur noch den Zwischenstand; der Integrationstest hatte dieselbe Abweichung gemeldet. Nach der Korrektur bestanden die Tests, und Opus hat den eingefrorenen Endstand erneut freigegeben. Der Ablauf einschließlich dieses Koordinationsfehlers bleibt nachvollziehbar dokumentiert.
