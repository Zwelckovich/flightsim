# Astra-Review des CSS-Beitrags von Opus

Stand: 24.09.2026. Gegenstand: vollständiger Diff von `v2/app.css` gegen den gesicherten Ausgangsstand und Integration mit dem aktuellen HTML/JavaScript. Der Implementierungslauf `ux-20260924-design` ist abgeschlossen. Die CSS-Datei bleibt seit dessen Übergabe unverändert.

## Entscheidung

CSS-Beitrag angenommen. Die vorhandene dunkle Instrumentenoptik bleibt erhalten. Die neue Navigation, größere beschriftete Leg-Ziele, Feldlabels, sichtbare Fokusmarkierungen und mobile Raster lösen die beobachteten Bedienprobleme. Keine zusätzlichen Bibliotheken oder Bilddateien nötig.

Gelesen wurden die tatsächlichen Änderungen, einschließlich Selektoren und Kaskade, Breakpoints, Farben, versteckten Zuständen, Karten-/Scrollregeln und Fokusdarstellung. Der wichtige `[hidden]`-Fix verhindert, dass CSS ein bewusst verstecktes Bedienelement sichtbar macht. Die mobilen Tabellen behalten ihren eigenen horizontalen Scrollbereich; die gesamte Seite läuft nicht über.

## Unabhängige Prüfung

- Build, JavaScript-Syntax, neue Navigationstests, bestehende Sync- und Szenerie-UI-Tests nach Zusammenführung erfolgreich.
- Browseransichten bei 1440 × 1000, 820 × 1180, 390 × 844 und 320 × 800 geprüft. Alle sechs Inhaltsreiter bei 320 px auf Seitenüberlauf geprüft: `scrollWidth === clientWidth` (305 px nach Scrollbar).
- Navigation auf Desktop einzeilig, auf Mobilgeräten zweizeilig; Reiter auf schmalen Bildschirmen in zwei Reihen. Lesbarkeit und Fokusdarstellung anhand von Screenshots geprüft.
- Vier Kartenansichten, H160-Briefing und Such-/Filterablauf funktionieren weiterhin. D3s Inline-Touch-Regel ist in der gebündelten Quelle bestätigt; die CSS-Ausnahme gilt ausschließlich außerhalb des Globusmodus.

## Kleine Integrationskorrekturen

Opus weist zutreffend auf die Namen der Zurück-/Weiter-Buttons und die fehlenden Rollen der beschrifteten Briefing-/Routencontainer hin. Diese HTML-Korrekturen übernimmt Astra nach Abschluss der unabhängigen Logikreview. Astra hat außerdem beobachtet, dass der Suchsprung die Reiter unter die klebende Navigation schieben kann; Scrollziel wird der Inhaltsbereich, Fokus bleibt im Suchfeld.

Die im kleinen Querformat nicht klebende Navigation ist akzeptiert: Auf niedrigen Bildschirmen bleibt mehr Platz für die eigentlichen Inhalte.

## Grenzen

Browserprüfung in Chromium/In-App-Browser, keine physische Touch-Hardware, kein Safari-/Firefox-Durchlauf. Globusgesten auf realem Touch-Gerät sind nicht geprüft. Kein vollständiger WCAG-Audit. Keine Live-Cloud- oder Simulatorprüfung.
