**Entscheidung: B1, B2 und B3 sind behoben. In den Korrekturen habe ich keine Fehler mehr gefunden, daher gebe ich sie frei. Offen ist nur Astras mobile Endabnahme.**

Ich habe nur statisch geprüft: Ich habe weder Tests noch einen Browser ausgeführt und die SHA-256-Werte nicht selbst berechnet. Die gelesenen Dateien entsprechen inhaltlich `corrections.diff`. Alle Laufzeitergebnisse stammen von Astra.

**B1** (`v2/app.js:801-813`, `1360-1362`)
- `stepLeg` merkt sich das fokussierte Element vor `select()` und prüft danach `disabled`. Das hält auch, wenn der Browser den deaktivierten Button vorher oder später selbst entfokussiert.
- Beim Mausklick ohne Fokuswechsel (macOS/iOS) ist `control` der `body`. Der Fokus bleibt dann, wo er war.
- `#jump` scrollt nur, der Fokus bleibt im Select.
- `openBriefing` fokussiert weiterhin `.grid`.

**B2** (`app.js:1377-1378`)
- Buttons und Links in `.grid` lösen die Kürzel wieder aus.
- `input`, `select` und `textarea` bleiben ausgeschlossen, auch `.copyarea`.
- Bei Pips greifen `defaultPrevented` bzw. die Prüfung auf body/`.grid`. Tabs sind zusätzlich über `[role=tab]` ausgeschlossen.
- Der neue Test würde fehlschlagen, wenn `button` wieder in die Liste käme.

**B3** (`app.js:846`, `861-867`)
- Die Reihenfolge wird vor `renderPlan` gesichert. Danach gilt: dieselbe Zeile, sonst die folgende, sonst die vorherige, sonst Reset.
- Bei „Offen“ oder „Geflogen“ ist `#clear-filters` im leeren Zustand sichtbar.
- `data-done` gibt es nur in `rowHtml`.
- `preventScroll` gilt nur, wenn dieselbe Zeile erhalten bleibt.
- Hat die Checkbox keinen Fokus, etwa nach Tippen unter iOS, ändert sich der Fokus nicht. `#q` wird auf diesem Weg nie fokussiert.

**Übrige Korrekturen ohne Befund**
- Suchsprung: Fokus auf `#q`, Scrollziel `#book`. Ist die Leiste nicht klebend, wird ihre Höhe nicht abgezogen.
- `td:first-child`: Es gibt keine verschachtelten Tabellen.
- Labels von `#q`, `#flt` und `#chsel`, „Zurück/Weiter“ sowie die Rollen region/group sind in Ordnung.

**Optional, kein Befund**
1. **Scroll-Versatz mit Safe-Area:** `reveal` (`app.js:804`) zieht nur die Höhe der Leiste ab, nicht ihr sticky `top: env(safe-area-inset-top)` (`app.css:114`, mit `viewport-fit=cover`).
   - Folge: Ist der obere Inset größer als 16 px, etwa bei einer iPhone-App vom Home-Bildschirm, liegt der Anker um „Inset − 16 px“ unter der Leiste.
   - Im normalen Browser ist der Inset vermutlich 0; das habe ich nicht geprüft.
   - Robuster wäre `parseFloat(getComputedStyle(bar).top)` plus die Höhe. Das ließe sich bei der Mobilabnahme mitprüfen.
2. **Label von `#jump`** (`template.html:36`): Es behält sein `aria-label`. Die sichtbare Beschriftung „Etappe x von y“ fehlt deshalb im zugänglichen Namen und wird beim Fokus nicht angesagt. Das war schon vorher so und betrifft die Korrektur nicht. Die Aussage „Sichtbare Formularlabels sind nun auch die zugänglichen Namen“ stimmt also nur für die Filterfelder.