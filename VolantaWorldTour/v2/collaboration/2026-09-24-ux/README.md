# Design- und Bedienungsreview – Weltreise ab Weeze

Geprüfte Anwendung: http://localhost:8000/ · 24.09.2026

## Befunde und Änderungen

| Beobachtung | Verbesserung |
|---|---|
| Zurück/Weiter und Leg-Auswahl erst unter dem langen Flugplan | Erreichbare Navigation am oberen Rand, Zielort in der Leg-Auswahl, gemeinsamer Etappenzähler für A320/H160, erstes offenes Leg und direkter Suchsprung |
| Kleine unbeschriftete Balken als Hauptnavigation | Ausklappbare Routenübersicht mit beschrifteten Legs und anklickbaren Kapiteln |
| Niedrige Kontraste und kleine Bedienziele | Hellere Hilfstexte, gut lesbarer Primärbutton, klare Fokusringe und größere Schaltflächen |
| Pfeiltaste auf Reiter wechselte versehentlich den Flug | Reiter mit eigener Pfeil-/Pos1-/Ende-Bedienung; Flugkürzel auf das Briefing begrenzt, Eingabefelder geschützt |
| Streckenauswahl in Tabellen nur mit Maus | Echte Schaltflächen in Flugplan und Szenerielisten, Fokus auf das geöffnete Briefing |
| Schwer verständliche leere Filterergebnisse | Trefferzahl oberhalb der Tabelle, erklärter Leerzustand und zentraler Filterreset |
| Suche nach mehreren Begriffen oder Namen ohne Akzente | Kombinierte Suche über Strecke, Orte, Länder, Kapitel und Flugzeug; Akzentnormalisierung und zusätzliche deutsche Ländernamen |
| Fokusverlust beim Aktualisieren von Fortschritt | Fokus nach Markieren wieder auf dem Button; in gefilterten Listen beim nächsten Treffer, sonst beim Filterreset |
| Wiederholte Bedienung der neuen Navigation verlor den Fokus | Select und Zurück/Weiter behalten den Fokus; auch der erste/letzte Flug wird sauber behandelt |

## Zusammenarbeit

Nach `M:\flightsim\cowork.md`: Ausgangsstand als Dateien und SHA-256 gesichert. Astra/Codex bearbeitete HTML, UI-Logik und Regressionstests; Claude Opus 5.5 mit `--effort max` ausschließlich das CSS. Eine separate Opus-Sitzung prüfte die mit Hashes eingefrorenen HTML-/Logikänderungen. Astra prüfte den tatsächlichen CSS-Diff und die zusammengeführte Oberfläche im Browser. Die drei relevanten Fokusbefunde wurden umgesetzt und durch zusätzliche Tests abgesichert. Keine gleichzeitige Bearbeitung derselben Quelldatei.

Die gezielte unabhängige Nachprüfung durch Opus hat B1/B2/B3 freigegeben. Alle drei Claude-Läufe meldeten das vorgesehene Modell, Max Effort, keinen Laufzeitfehler und keine verweigerten Werkzeuge. Die abschließende Neuerzeugung stimmt mit den eingefrorenen Review-Hashes überein; `localhost:8000` liefert exakt diese HTML-Datei.

Aufträge und Nachweise liegen unter `M:\flightsim\VolantaWorldTour\v2\collaboration\2026-09-24-ux`. Rohprotokolle verbleiben im bereits ignorierten `.runs`-Verzeichnis.

## Prüfungen

Automatisiert: Build, JavaScript-Syntax, die 16 vorhandenen Sync-Szenarien, Szenerie-Rendering, Debrief-/Szeneriedatenprüfungen und neue Regressionen zu Suche, Filtern, Tastatur und Navigationsgrenzen.

Browser: Navigation und Briefing-Sprung, kombinierte Suche, Reiter-Pfeile, aufgeklappte Route, H160-Etappe, vier Kartenansichten, Speichern/Neuladen und Geflogen-Filter. Zusätzlich wiederholte native Select-/Button-Bedienung, Fokus an der letzten Etappe, Briefing-Kürzel und der Suchsprung. Fortschrittsänderungen erfolgten ausschließlich an einem separaten lokalen Testursprung; die Testmarkierungen wurden aufgehoben.

Visuelle Prüfung bei 1440 × 1000, 820 × 1180, 390 × 844 und 320 × 800 sowie kleinem Querformat 740 × 420. Alle sechs Inhaltsbereiche ohne horizontalen Seitenüberlauf bei 320 px; breite Tabellen scrollen innerhalb ihres eigenen Bereichs. Keine JavaScript-Fehler in der abschließenden Browserprobe. Unabhängig nachgerechnet: Primärbutton 6,35:1 und gedimmter Text auf dem Feldhintergrund 4,69:1.

Route, Content, Debriefings, aggregierte Tourdaten und Build-Quelle sind laut SHA-256 unverändert. Die lokale HTML-Datei und das Artifact wurden aus den geprüften Quellen neu erzeugt.

## Umfang und Grenzen

Die Änderungen betreffen die lokale Oberfläche und ihre generierten HTML-Ausgaben. Keine Veröffentlichung des privaten Online-Artifacts, kein Commit/Push. Die echte Artifact-Datenbank und der Flugsimulator sind nicht Bestandteil dieser UI-Abnahme; der vorhandene Cloud-Abgleich wird mit isolierten Regressionstests geprüft. Browserprüfung in Chromium, kein vollständiger WCAG-Audit, kein Safari-/Firefox-Durchlauf und keine physische Touch-Hardware. Erweiterte Umschrift von Sonderzeichen wie ø und Firefox-spezifische Formularwiederherstellung bleiben optionale Folgearbeiten.
