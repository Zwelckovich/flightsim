# Unabhängige Review: eingefrorene UI-Logik und HTML

Projekt: M:\flightsim\VolantaWorldTour. Modell: Claude Opus 5.5 mit Max Effort.
Arbeite nach M:\flightsim\cowork.md. Dies ist ein begrenzter Read-only-Review-Auftrag, keine Implementierung. Keine Unteragenten, keine Shell, kein Commit/Push, keine Änderungen. Kein Web nötig.

## Exakt eingefrorener Umfang
Prüfe ausschließlich die Änderungen in v2/app.js, v2/template.html und den neuen Regressionstest v2/tests/check_ui_navigation.cjs. Ausgangsstand: v2/collaboration/2026-09-24-ux/baseline/v2/app.js und template.html. Diff: v2/collaboration/2026-09-24-ux/behavior-review.diff. SHA-256: behavior-review-manifest.json im selben Ordner. Diese Dateien werden bis zu deiner Übergabe nicht geändert.

Ein anderer separater Opus-Auftrag gestaltet gerade ausschließlich app.css, nach dem Vertrag in opus-design.md im selben Ordner. CSS und erzeugte HTML-Ausgaben sind ausdrücklich NICHT Gegenstand deiner jetzigen Review; sie sind noch nicht eingefroren. Astra prüft den CSS-Beitrag nach dessen Übergabe unabhängig und integriert ihn mit diesem eingefrorenen Verhalten. Du musst die CSS-Aufgabe nicht erneut bearbeiten. Das vermeidet die Review eines unfertigen Gesamtstands.

## Nutzerziel / feste Regeln
Design und Bedienung der bestehenden lokalen Worldtour verbessern, Instrumentenstil erhalten. Vorhandene Route, Content, IDs, Fortschritt, Cloud-Sync, Backups und Debriefings erhalten. Der Code wird in eine lokale HTML und ein separates Artifact eingebettet. Quelle ist v2; keine Datenänderung beabsichtigt. Keine AGENTS.md/CLAUDE.md im Projekt gefunden. Bestehende V2-Dateien waren untracked und wurden gesichert, nichts zurückgesetzt.

## Änderungen
Navigation oben: vorher/nächster Flug, Sprungliste mit Zielort, erstes offenes Leg, Suchsprung. Ausklappbare Kapitelroute mit nummerierten Pips und nur einem Tabstop. Native Buttons für die Streckenauswahl in Plan und Szenerielisten. Suchbegriffe kombiniert, Akzente normalisiert, deutsche Ländernamen zusätzlich über Intl.DisplayNames. Trefferzahl/Leerzustand/Filterreset. Tab-Pfeile/Home/End getrennt von globalen Leg-Kürzeln; keine Kürzel in interaktiven Feldern oder bei Autorepeat. Checkbox-Klickflächen dürfen keinen Leg-Sprung auslösen. Fokus nach Re-Rendering des Geflogen-Buttons oder gefilterter Checkbox wiederherstellen. Leg-Links per Hash, auch ungültiges URI-Escaping robust. Sticky-Navigationshöhe beim Fokus-/Scrollsprung berücksichtigen.

## Schon geprüfte Evidenz
Astra hat node --check app.js, die 16 bestehenden check_sync.cjs-Szenarien, check_scenery_ui.cjs und den neuen check_ui_navigation.cjs ausgeführt: PASS. Debrief-/Szeneriedatenprüfungen liefen ebenfalls zuvor erfolgreich. Browser am isolierten Ursprung 127.0.0.1:8765: Tab-Pfeile wechseln Bereich ohne Leg-Wechsel; Markieren bleibt nach Reload erhalten; erstes offenes Leg springt korrekt; Checkbox im Geflogen-Filter entfernt Treffer ohne Leg-Sprung und setzt Fokus auf q; Route per Enter und Rail-Pfeile funktionieren; vier Kartenmodi und H160-Sprung funktionieren. Diese Browserproben liefen vor den letzten kleinen Änderungen (zusätzliche deutsche Suchnamen, globale Kürzel auf Briefing begrenzt, Auswahlhinweis entfernt); diese letzten Änderungen sind durch Node-Prüfungen abgedeckt und werden nach CSS-Übergabe noch einmal im Browser geprüft.

## Gesuchte Befunde
Lies tatsächliche Änderungen, prüfe auf konkrete Regressionen/Bedienfehler: doppelte Click-Auslösung, Checkbox/Label-Bubbling, Tastatur/Fokus, Suchreset, Zustandskonsistenz, kompatible bestehende Runtime/Tests. Keine allgemeine Wunschliste und kein Gesamtaudit von Cloud/Recherche. Nenne nur relevante, belegte Befunde mit Datei und Stelle, Auswirkung und Reproduktion. Widerspruch zu Änderungen ist ausdrücklich erlaubt. Unterscheide echten Fehler von optionalem Komfort. Wenn keine wesentlichen Befunde: klar sagen. Behaupte keine selbst ausgeführten Shell-/Browsertests; nur statische Review.

Gib einen knappen Übergabebericht als finale Antwort aus; der Runner speichert ihn. Ziel: Entscheidung, ob diese eingefrorenen Logik-/Markup-Änderungen freigegeben werden können, und gegebenenfalls konkrete notwendige Korrekturen.
