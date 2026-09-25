# Gezielte Nachprüfung der Review-Korrekturen

Du bist Opus 5.5 mit Max Effort. Lies nur zur gezielten Nachprüfung; keine Dateien ändern, keine Unteragenten, kein neuer Gesamtaudit oder Web-Recherche. Antworte bitte mit maximal 450 Wörtern: je F1–F4 behoben/offen, ggf. konkreter verbleibender Fehler, Freigabe dieser Änderungen oder begründete Ablehnung. Prüfe den tatsächlichen Code unabhängig.

Projekt M:/flightsim/VolantaWorldTour. Der vorherige Opus-Review steht in v2/collaboration/2026-09-24/opus-review-astra-result.md. Die fünf relevanten Dateien sind jetzt eingefroren; SHA-256 stehen in astra-review-candidate.json. astra-changes.patch wurde aktualisiert.

## Gezielter Umfang

- F1: v2/app.js queue/pushMark/pushVol/pushEpochs. Zusätzlich zu pendingWrites merkt confirmedWrites pro Schlüssel alle erfolgreich bestätigten Versionen. Ein später Snapshot erzeugt kein weiteres identisches Dokument. Ein fehlgeschlagener Upload wird nicht als bestätigt markiert. Prüfe speziell diesen Ablauf; append-only Events, deterministische Vergleiche und Reset-Journal wurden im ersten Review bereits als richtig bewertet.
- F2: v2/tests/make_sync_tests.py wurde schon während des ersten Reviews angepasst: uploadedLegs() nutzt Dokumentdaten, keine festen IDs. Zwei zusätzliche Browserszenarien für Event-IDs und unabhängige Reset-Einträge. Der ursprüngliche Finding-Text zitiert hier einen inzwischen veralteten Zwischenstand.
- F3: renderScn bezieht nun XC[l.x].fallback.anchor/target in die Kapitel-Sim-Prüfungen ein (als Ausweichziel gekennzeichnet, nicht in die Downloads). renderXcards zeigt den Hinweis ebenfalls am Ausflug. Prüfe FMZJ.
- F4: simCheckNote zeigt nun Quellenlinks, durch esc geschützt. UI-Test prüft Quellen und FMZJ im Kapitel.

Zusätzlich kleine UI-Korrekturen aus deinem Review: Karten zeigen alle Items; owned/hand/stdok zeigen Installationshinweise; hand/stdok-Hinweise erscheinen in der Vorbereitung; alt ist als Alternative beschriftet; Hauptpakete werden als zusätzliche Empfehlungen gezählt; Labels sagen recherchiert; ungültige dependency-Elemente werden gefiltert. Der Opus-Datenlauf läuft parallel, seine Build-/Datendateien gehören nicht zu deiner Nachprüfung.

Astra hat node --check v2/app.js sowie 16 Sync-Tests und den UI-Renderingtest erfolgreich ausgeführt. Darunter zwei neue Fälle: set() bestätigt, Snapshot bleibt zurück; und Schreibfehler mit später erfolgreichem Retry. Du hast nur Lesetools und sollst keine eigenen Testläufe behaupten. Die private echte Cloud und das visuelle Browserlayout sind hier nicht überprüfbar und bleiben dokumentierte Grenzen.
