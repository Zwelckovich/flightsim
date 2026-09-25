Ich habe `v2/app.css` überarbeitet; keine andere Datei ist geändert. Getestet ist nichts: Ich hatte keine Shell und keinen Browser. Alle Angaben unten beruhen auf dem Code und berechneten Werten, Build und Browserprüfung liegen bei dir, Astra. Das CSS habe ich gegen den Stand von `template.html` und `app.js` geprüft, den ich während deiner laufenden Arbeit gelesen habe. Alle Vertragsklassen und -IDs waren dort schon vorhanden.

## Änderungen in `v2/app.css`

**Grundlagen**
- **Kontraste:** Hilfstext `--tx3` jetzt `#aab5be`, gedimmter Text `--tx4` jetzt `#919da8`. Das alte `--tx4` hatte auf dem Panelhintergrund nur 3,1:1, das neue liegt überall bei mindestens 4,69:1.
- **Primärbutton:** Dunkler Text `--on-lead: #04121b` auf dem unveränderten Cyan, fett. Kontrast 6,35:1 statt 2,99:1 mit Weiß.
- **Fokusring:** Einheitlich 2 px in `#66ccff` (9,9:1 auf dem Seitenhintergrund) statt 40 % transparentem Cyan.
- **Feldrahmen:** Neue Farbe `--bd4`, 3,67:1 zum Seitenhintergrund.
- **`[hidden]`** gewinnt jetzt gegen alle `display`-Regeln. Das behebt nebenbei einen bestehenden Fehler: `#rs-step1` blieb bisher sichtbar, obwohl es versteckt war.
- **`--nav-h`** speichert die Höhe der Leiste: 62 px, unter 760 px Breite 110 px, im kleinen Querformat 0. Die Seite hält damit Fokus- und Sprungziele unterhalb der sticky Leiste frei.
- `.wrap` berücksichtigt die Ränder von Notch-Geräten.
- **Skip-Link** erscheint nur beim Fokus.

**Leg-Navigation**
- **Desktop:** Eine Zeile mit Zurück, Leg-Auswahl, Weiter und rechts den beiden Schnellaktionen. Die Schnellaktionen sind als Outline-Buttons optisch zurückgenommen.
- **Positionsanzeige:** „Etappe x von y“ steht als kleine Beschriftung im oberen Teil des Auswahlfelds. So bleibt die Leiste einzeilig.
- **Unter 760 px:** Zwei Zeilen – oben Zurück/Auswahl/Weiter, darunter die Schnellaktionen als zwei gleich breite Buttons. Höhe etwa 109 px.
- **Bis 479 px:** Zurück/Weiter werden zu einem Pfeil mit kleiner Beschriftung darunter. Die Auswahl hat dann auf 390 px etwa 258 statt 183 px Platz.
- **Querformat klein (unter 760 × 520 px):** Die Leiste klebt dort bewusst nicht oben, weil sie sonst rund ein Drittel des Bildschirms belegen würde. Das weicht von „bleibt sticky“ ab; wenn du das nicht willst, genügt es, diese eine Media-Query zu entfernen.

**Routenübersicht**
- Aufklappleiste mit 44 px Höhe und gezeichnetem Pfeil (kein Textzeichen, das Screenreader mitlesen). Derselbe Pfeil gilt für `details.chk` und `.time-info`.
- Das horizontale Scrollen bleibt lokal in der Leiste; Fokusringe werden am Rand nicht abgeschnitten.
- **Pips:** A320 34 × 36 px, H160 als Pille mit mindestens 30 × 30 px und passender Breite für Labels wie „BORABORA-1“.
  - Zustände: geflogen grün mit weißer Nummer, aktuell Cyan mit dunkler Nummer, lange Legs mit orangem oberem Streifen.
  - Der Hover-Effekt greift nur bei Mausbedienung.
- Kapitelüberschriften sind Buttons mit mindestens 32 px Höhe.

**Karte**
- Die Kartenhöhe ist auf den sichtbaren Bereich unter der Leiste begrenzt (mindestens 240 px). Das Bild skaliert mittig, die freien Ränder sind schwarz wie der Kartenhintergrund.
- **Touch:** d3-drag setzt auf Touch-Geräten inline `touch-action: none` (im gebündelten d3 nachgesehen). Dadurch blockiert die Karte das Scrollen der Seite. Außer beim Globus hebe ich das per `!important` auf.
- Ansichtsumschalter 40 px hoch, der gewählte Knopf mit Cyan-Unterstrich, Fokusring nach innen; unter 520 px als vier gleich breite Spalten.

**Bedienelemente**
- `.btn` mindestens 44 px, `.btn.small` 36 px, in Toolbars und auf Touch-Geräten 44 px.
- Reiter 44 px hoch; unter 720 px als Raster mit 3 × 2 Feldern.

**Filter und Tabelle**
- Filterfelder mit Beschriftung über dem Feld, 44 px hoch; unter 600 px volle Breite. Die Auswahlfelder haben einen eigenen Pfeil ohne Bilddatei.
- `.plan-summary`: Trefferzahl links, Hinweis rechts.
- Tabelle:
  - Die Häkchen-Trefferfläche ist 40 × 40 px, das Kästchen selbst 18 px.
  - `.route-link` ist als Link gestaltet.
  - Die ausgewählte Zeile hat zusätzlich einen Cyan-Balken links.
  - Nur Zeilen mit `data-leg` oder `data-go` zeigen Zeiger-Cursor und Hover.
  - Der Leer-Hinweis bleibt auch auf dem Handy ohne seitliches Scrollen lesbar.

**Reflow bis 320 px**
- Alle Kartenraster wie `minmax(300px, 1fr)` sind auf `minmax(min(100%, …), 1fr)` umgestellt.
- Die Zählerzeile im Kopf darf umbrechen; bisher lief sie ab etwa 385 px über den Rand.
- Toasts sind auf die Bildschirmbreite begrenzt.
- `.wrap`-Innenabstand unter 400 px auf 12 px.

**Aufgeräumt**
- Tote Regeln entfernt: `.catc.done`, `.catc.heli`, `footer select`, `.toolbar .hint`.
- Die doppelte `.catc`-Definition ist in einem Abschnitt zusammengeführt.

**Zusätzlich**
- Auf Touch-Geräten 16 px Schrift in Feldern, damit iOS beim Antippen nicht hineinzoomt.
- Ein kleiner Block für den Windows-Kontrastmodus.
- Die Einstellung für reduzierte Bewegung gilt weiter.

## Statisch geprüft
- Keine Build-Platzhalter und kein `</style>` im CSS (der Build ersetzt Text).
- `!important` nur bei `[hidden]`, der Karten-Korrektur und den vorher schon vorhandenen Stellen.
- `:has()` steht nur in eigenständigen Regeln; ältere Browser verlieren also nur diese Zusatzfunktion.
- Reihenfolge und Spezifität geprüft: Die Sonderregeln für die Leg-Auswahl stehen nach den gemeinsamen Feldregeln, „aktuell“ gewinnt gegen „geflogen“, Hover funktioniert bei deaktivierten Buttons nicht.
- Breiten der Leiste bei 320, 390, 480 und 760 px mit Arial-Maßen durchgerechnet: kein Überlauf.
- Kontraste nach der WCAG-Formel berechnet.

## Grenzen
- Bitte im Browser prüfen:
  - Breiten 320, 360, 390, 480, 760, 1024 und 1366 px.
  - Die senkrechte Lage des Leg-Textes unter der Beschriftung in Safari und Firefox.
  - Auf einem Touch-Gerät: Seite scrollt über der Karte, Antippen von Legs und Flughäfen funktioniert weiter, Globus lässt sich ziehen.
- Die Schriftbreiten sind geschätzt; ob Arial Narrow bzw. Barlow verfügbar ist, verschiebt sie.
- Unter 480 px stehen „Zurück“ und „Weiter“ fest im CSS. Wenn sich die Buttontexte ändern, muss das CSS mitgeändert werden.
- Die Tabelle scrollt auf dem Handy weiter seitlich (Mindestbreite 760 px), weil ihre Struktur erhalten bleiben sollte.
- Die Klickflächen für Legs und Flughäfen in der Karte habe ich nicht verändert; sie bleiben auf dem Handy klein.

## Hinweise zu deinen Dateien (nicht geändert)
1. `#prev`/`#next` haben `aria-label` „Vorheriges/Nächstes Leg“. Der Name enthält damit nicht den sichtbaren Text „Zurück/Weiter“ (WCAG 2.5.3, Sprachsteuerung).
2. `div.grid` und `div.rail` haben ein `aria-label`, aber keine Rolle. Solche Labels werden oft ignoriert; eine Rolle wie `region` bzw. `group` ergänzen oder das Label entfernen.
3. `reveal()` zieht die Leistenhöhe auch ab, wenn die Leiste im Querformat nicht klebt. Das ergibt nur einen etwas größeren Abstand und ist unschädlich.