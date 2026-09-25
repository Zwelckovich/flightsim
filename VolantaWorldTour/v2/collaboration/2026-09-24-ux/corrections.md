# Korrekturen nach der unabhängigen Review

## Umgesetzt

- **B1 (Fokus in Navigation):** Scrollen und Fokuswechsel getrennt. Select und Navigationsbuttons behalten ihren Fokus; an der Grenze wird der gerade deaktivierte Button durch den Select als Fokusziel ersetzt. Route-/Kapitel-/Resume-Sprünge fokussieren weiterhin das Briefing.
- **B2 (Briefing-Kürzel):** Buttons und Links innerhalb des Briefings erlauben wieder Links/Rechts/G. Eingabefelder, Tab-/Rail-Handler und Bedienelemente außerhalb des Briefings bleiben geschützt. Browserreproduktion vor und nach der Korrektur bestätigt.
- **B3 (gefilterte Checkliste):** Fokus bleibt in der Ergebnisliste: gleicher, nächster, sonst vorheriger Treffer; ohne Treffer auf Filterreset. Browserprobe bestätigt den nächsten Treffer und den Leerzustand. Testmarkierungen danach aufgehoben.
- **Integrationsbefund von Astra:** Der Suchsprung hält die Reiter unter der Sticky-Navigation sichtbar. Desktop gemessen 76,95 px Reiteroberkante bei 60,67 px Navigationsunterkante; bei 320 px entsprechend 124,84 / 108,67 px.
- **Semantik:** Benannte Container erhalten region/group; Zurück/Weiter bleiben Teil der zugänglichen Namen. Die sichtbaren Filterlabels bestimmen nun auch die zugänglichen Namen.
- **Checkbox-Zelle:** Der gesamte erste Tabellenbereich öffnet beim Klicken neben dem Häkchen kein Briefing.
- **Kleines Querformat:** Eine nicht klebende Navigationsleiste zählt nicht mehr als Scrolloffset.

## Bewusst beibehalten / abgegrenzt

- Der ausdrücklich gewählte Filterreset führt weiter in die Suche. Das unterstützt die nächste Suche; automatisches Abhaken einer Liste öffnet dagegen kein Textfeld mehr.
- Kapitel-Buttons sind zusätzlich zu einem einzigen Pip-Tabstop erreichbar. Das ist beabsichtigt, damit Kapitel direkt mit der Tastatur auswählbar bleiben.
- `aria-pressed` kommuniziert den Geflogen-Status, der sichtbare Text bleibt ebenfalls verständlich. Kein schwerwiegender Fehler festgestellt.
- Erweiterte Umschrift für ø/æ/ð/ł und Firefox-spezifische Formularwiederherstellung sind optionale Folgearbeiten. Die vorhandene NFD-Suche deckt kombinierbare Akzente und ß ab. Kein umfassender Internationalisierungs-/Cross-Browser-Audit behauptet.

## Nachweise

`corrections.diff` wird gegen den vorherigen, mit SHA-256 verifizierten Reviewstand erstellt. `correction-review-manifest.json` hält den endgültigen eingefrorenen Stand fest. `validation.json` enthält die erfolgreichen letzten Testläufe. Die Nachprüfung erfolgt durch `ux-20260924-correction-review` auf Claude Opus 5.5 mit Max Effort.
