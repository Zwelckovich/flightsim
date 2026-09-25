# Review der eingefrorenen UI-Logik und des HTML (app.js, template.html, check_ui_navigation.cjs)

**Entscheidung: Freigabe, sobald B1 und B2 korrigiert sind (beides kleine Änderungen). B3 empfehle ich im selben Durchgang.** Doppelte Klick-Auslösung, Label-Bubbling, Suchreset und Test-/Runtime-Kompatibilität habe ich ohne Befund geprüft.

Das ist eine rein statische Review. Ich habe keine Shell, keinen Browser und keine Tests ausgeführt und die SHA-256-Werte nicht selbst berechnet. Die gelesenen Dateien stimmen inhaltlich mit `behavior-review.diff` überein; verglichen habe ich mit der Baseline.

## Notwendige Korrekturen

**B1 – Die obere Navigation nimmt ihren eigenen Bedienelementen den Fokus weg** (`v2/app.js:1347-1349` zusammen mit `reveal()` in `app.js:801-805`)
`#prev`, `#next` und `#jump` rufen `reveal($('.grid'))` auf. Dadurch springt der Fokus bei jeder Aktivierung auf `.grid`. In der Baseline blieb er auf dem Element.
- **`#jump`:** In Chrome, Edge und Firefox (ab Version 63) unter Windows lösen ↑/↓ und die Tippsuche bei geschlossener Liste sofort `change` aus. Nach dem ersten Schritt ist die Liste deshalb nicht mehr fokussiert.
  - Reproduktion: Mit Tab auf „Zu einem Leg springen“ gehen und ↓ drücken. Das nächste Leg erscheint, der Fokus liegt aber im Briefing. Ein weiteres ↓ scrollt nur die Seite.
  - Tippt man „050“, springt die Liste um genau einen Eintrag, weil nur die erste „0“ ankommt.
- **`#prev`/`#next`:** Enter oder Leertaste wirkt auf „Weiter →“ nur einmal. Screenreader-Nutzer müssen nach jedem Schritt zum Button zurücknavigieren.
- **Korrektur:**
  - Für diese drei Handler nur scrollen, den Fokus nicht verschieben, z. B. über `reveal(el, focus = true)` und hier `false` übergeben.
  - Wird ein Button an der ersten oder letzten Etappe `disabled`, den Fokus auf den Gegenbutton oder auf `.grid` setzen.
  - `openBriefing` (Route-Links, Kapitel, Resume) darf den Fokus weiter verschieben, denn das sind einmalige Sprünge.

**B2 – ←/→/G funktionieren nicht mehr, wenn ein Button im Briefing fokussiert ist** (`app.js:1364`)
- **Ursache:** Die Ausschlussliste in Zeile 1364 enthält `button, a`, obwohl Zeile 1365 die Kürzel ohnehin auf `body`/`.grid` begrenzt.
- **Folge:** Nach „Als geflogen markieren“ setzt `refreshProgress` den Fokus jetzt ausdrücklich auf `#flownbtn` zurück (`app.js:849`), und danach bewirken ←/→/G nichts. Dasselbe passiert nach einem Klick auf Leg/Kapitel/Welt/Globus oder die Debrief-Vorlage, denn unter Windows bekommen Buttons beim Klick den Fokus.
- **Vergleich:** In der Baseline funktionierten die Tasten hier. Das Verhalten widerspricht außerdem dem Fußzeilenhinweis „im Briefing: Legs blättern“ (`template.html:169`).
- **Reproduktion:** Ein Leg öffnen, „Als geflogen markieren“ klicken, → drücken: Das Leg wechselt nicht.
- **Korrektur:** `button, a` aus der Liste in Zeile 1364 streichen.
  - Tabs, Pips, Navigation und Plan liegen außerhalb von `.grid` und bleiben über Zeile 1365, `[role="tab"]` bzw. `defaultPrevented` ausgeschlossen.
  - Kein Button oder Link in `.grid` hat eine eigene Pfeiltasten-Funktion.
  - Im Test einen Fall ergänzen: Button in `.grid` fokussiert, ArrowRight wechselt das Leg.

## Empfohlen (im selben Durchgang)

**B3 – Nach einer gefilterten Checkbox landet der Fokus im Suchfeld** (`app.js:850-853`)
Bei Filter „Offen“ oder „Geflogen“ verschwindet die abgehakte Zeile, und der Fokus springt mit `preventScroll` auf `#q`.
- **Tastatur:** Der Fokus springt unsichtbar an den Tabellenanfang. Die Position in der Liste ist verloren: Bis zur nächsten offenen Zeile sind es 2 Tabstopps pro vorheriger Zeile.
- **Touch-Geräte:** Wo die angetippte Checkbox den Fokus bekommt (z. B. Chrome/Android), öffnet der Fokus auf das Suchfeld wahrscheinlich die Bildschirmtastatur. Das ist abgeleitet, nicht getestet.
- **Korrektur:**
  - Vor `renderPlan` die Leg-IDs der Zeilen merken.
  - Danach die Checkbox der nächsten noch vorhandenen Zeile fokussieren, sonst die der vorherigen.
  - Ist die Liste leer, auf `#clear-filters` gehen; der Button ist dann sichtbar und ist kein Textfeld.

## Optional / geringfügig
- **Suche** (`app.js:35`): NFD zerlegt ø/æ/ð/đ/ł nicht. In den Daten kommen Tromsø, Bodø, Rønne und „Ruđer Bošković“ vor; „tromso“, „bodo“ oder „ronne“ finden deshalb nichts. Nach `toLowerCase()` abbilden: ø→o, æ→ae, ð/đ→d, ł→l, þ→th, œ→oe.
- **Sichtbare Labels vs. `aria-label`** (`template.html:92/93/107`): `aria-label` überschreibt die neuen sichtbaren Labels. Für `#flt` lautet der Name „Filter“, sichtbar steht „Status und Interessen“ (WCAG 2.5.3). Die `aria-label` an #q/#flt/#chsel entfernen.
- **`aria-label` auf generischen `div`s:** Auf `div.grid` (`template.html:52`) und `div#rail` (`template.html:47`) ist `aria-label` nach ARIA 1.2 unzulässig. `.grid` bekommt besser `role="region"`, damit der Name beim Fokussprung angesagt wird.
- **`#flownbtn`** (`app.js:473`): `aria-pressed` und der wechselnde Text führen zu einer doppelten Zustandsansage („✓ Geflogen, gedrückt“). Eines von beiden reicht.
- **Zeilenklick** (`app.js:1315`): Ausgenommen ist nur `.check-hit`. Ein Fehlklick in das Innenpolster der Checkbox-Zelle öffnet das Briefing und scrollt nach oben. Die ganze erste Zelle auszunehmen macht das unabhängig vom CSS.
- **„Filter zurücksetzen“** fokussiert `#q`; auf Mobilgeräten öffnet sich dabei die Tastatur. `#flt` wäre ein neutralerer Fokusziel.
- **„Nur ein Tabstop“** gilt für die Pips. Die 28 Kapitel-Buttons sind zusätzliche Tabstopps; wenn das gewollt ist, nur die Beschreibung anpassen.
- **Schon vor der Änderung vorhanden:** Firefox stellt beim Neuladen die Werte von #q/#flt wieder her, `state` bleibt aber auf „all“. Dann widersprechen sich Anzeige, „Filter aktiv“ und der Reset-Button. Abhilfe: `autocomplete="off"` oder den Zustand beim Start aus dem DOM lesen.

## Ohne Befund geprüft
- **Klickpfade:**
  - Route-Link im Plan: tbody ignoriert `button`, `document` öffnet genau einmal. Zeilenklick öffnet ebenfalls einmal.
  - Szenerietabellen (`tr[data-go]` mit Button) lösen einen Aufruf aus. Kapitel-Button und Pip kommen sich nicht in die Quere, `#flownbtn` ebenfalls nicht.
- **Label-Bubbling:** Ein Klick auf `label.check-hit` wird von tbody ignoriert. Der anschließende Input-Klick ruft genau einmal `setFlown` mit schon umgeschaltetem `checked` auf. Dass die Zeile während der Ereignisverarbeitung entfernt wird, löst keinen zweiten Aufruf aus.
- **Tabs:** Roving tabindex, Pfeile/Pos1/Ende; durch `preventDefault` und `[role=tab]` kein Leg-Wechsel.
- **Rail:** Ein Pip-Tabstop, `aria-current`, kein doppelter Schritt. Die Rail-Reihenfolge entspricht der LEGS-Reihenfolge (an Kapitel 01 geprüft). `toggle` scrollt zum aktuellen Pip.
- **Modifier/Autorepeat:** Alt/Strg/Meta und `ev.repeat` werden korrekt ausgefiltert.
- **Suche und Filter:**
  - Begriffe werden UND-verknüpft; der Debounce wird beim Reset abgebrochen; Trefferzahl, Leerzustand und `hidden` sind konsistent.
  - Alle 245 Kategorie-Codes sind wohlgeformte 2-Buchstaben-Regionen, `Intl.DisplayNames.of` wirft also nicht. Die sichtbaren `CATN`-Namen bleiben unverändert.
- **Hash:** `decodeURIComponent` ist beim Start und in `hashchange` abgesichert. `replaceState` löst kein `hashchange` aus. Leg-IDs kollidieren mit keiner Element-ID. Der Skip-Link verhindert den Hash-Wechsel.
- **Zustand und Selektoren:** `updateNav` in `refreshProgress` hält „Erstes offenes Leg“ und die Positionsanzeige bei Sync, Import und Reset aktuell. Alle neu referenzierten Selektoren existieren im Template.
- **Kompatibilität:**
  - Die Platzhalter für `build_v2.py` sind unverändert.
  - Der Ausschnitt, den `check_sync.cjs` aus app.js übernimmt (bis zum Abschnitt „Prosa“), läuft mit `CAT_SEARCH`/`Intl` im vm-Kontext.
  - `check_scenery_ui.cjs` ist nicht betroffen. `make_sync_tests.py` nutzt nur unveränderte IDs und einen eindeutigen Speicherschlüssel.
- **Neuer Test:**
  - Die Funktionsextraktion über `\n  }` passt für die gewählten Funktionen. Der „Deutschland“-Treffer setzt Full-ICU voraus, was in Node Standard ist.
  - Nicht abgedeckt sind `#jump`/`#prev`/`#next`, `openBriefing`, Fokuswiederherstellung und `hashchange`. Nach B1/B2 wäre dort jeweils ein Fall sinnvoll.

## Hinweis für die CSS-Integration (nicht Teil dieser Review)
- Ein programmatischer Fokus auf `.grid` nach einer Tastaturaktion kann `:focus-visible` auslösen, also einen Rahmen um Briefing und Karte zeichnen.
- Natives Scrollen per Tab oder Fokus unter die sticky Stepbar deckt `reveal()` nicht ab. Dafür wäre `scroll-padding-top` nötig.