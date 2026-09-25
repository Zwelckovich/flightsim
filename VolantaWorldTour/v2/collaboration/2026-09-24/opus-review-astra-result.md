# Review von Astras V2-Änderungen (nur gelesen, Opus 5.5)

**Geprüfter Stand:** `v2/app.js` hat sich während des Reviews geändert. Geprüft habe ich den aktuellen Code:
- Jede Änderung wird als neues Dokument angelegt (`eventKey`) statt ein bestehendes zu überschreiben.
- Doppelte Uploads werden über `pendingWrites` unterdrückt.
- Resets landen in einer eigenen Collection `resets`.
- `check_sync.cjs` hat 14 Szenarien.

`astra-changes.patch` zeigt noch die Vorversion mit einem überschriebenen Dokument pro Leg und `localeCompare`. Der Patch passt also nicht mehr zum Code und sollte neu erzeugt werden. Ich habe keine Tests ausgeführt und keine Dateien geändert.

Drei Probleme der Patch-Fassung behebt der aktuelle Code bereits, sie sind keine Findings mehr:
- Massenhaft doppelte Uploads beim Import
- Abhängigkeit davon, dass das Gerät mit dem neuesten Stand noch offen ist
- Gleichstände, die je nach Spracheinstellung des Geräts anders aufgelöst werden

## Sync: Gesamtbewertung

- **Korrektheit:** Pro Leg bzw. Kategorie gewinnt der neueste Wert über alle Dokumente, alte und neue (`v2/app.js:169-210`). Dieser Wert kann in der Cloud nur steigen, lokal ebenfalls. Hochgeladen wird nur, wenn der lokale Wert strikt neuer ist.
- **Keine Endlosschleife:** Solange ein Snapshot alle Dokumente enthält, gibt es keine sich selbst erhaltende Uploadschleife.
- **Reset-Rennen:** Reset-Dokumente haben feste IDs (`v2/app.js:162-168`) und werden per Maximum zusammengeführt (`v2/app.js:235-246`). Ein verspäteter älterer Reset senkt nichts. Gleichzeitige Resets verschiedener Felder bleiben beide erhalten.
- **Gerät mit neuestem Stand geschlossen:** robust, sofern dessen Schreibzugriff den Server erreicht hat.

## Echte Findings (vor Abnahme beheben)

**F1 – Dauerhafte doppelte Dokumente nach bestätigtem Schreiben (abhängig vom DB-Verhalten)**
- **Stelle:** Die Sperre gegen doppelte Uploads endet, sobald der Schreibzugriff abgeschlossen ist (`.finally`, `v2/app.js:124-127`). Jeder erneute Upload bekommt einen neuen Zufallsschlüssel (`v2/app.js:150-152`, `158-160`).
- **Auslöser:** Man stellt eine Sicherung mit vielen Legs wieder her (`v2/app.js:1127-1133`). Die DB bestätigt `set()`, bevor der Snapshot mit diesem Dokument eintrifft. Kommt dazwischen ein Snapshot eines anderen Legs, fehlt das Dokument dort noch. Die Sperre ist aber schon weg, also schreibt `pushMark` ein inhaltsgleiches zweites Dokument, das dauerhaft bleibt.
- **Schlimmster Fall:** Enthält ein Snapshot je nicht alle Dokumente (Limit, Paginierung, Cache), erzeugt jeder Snapshot ein neues Dokument. Das löst wieder einen Snapshot aus, und die Collection wächst ohne Grenze.
- **Warum die Tests das nicht sehen:** `v2/tests/check_sync.cjs:198-206` prüft nur, solange Schreibzugriffe zurückgehalten werden. Der Browser-Mock benachrichtigt direkt innerhalb von `set` (`v2/tests/make_sync_tests.py:38`).
- **Abhilfe (klein, kompatibel):** Neue Dokumente werden nie überschrieben. Ein schon bestätigtes, identisches Dokument erneut zu senden ist also nie nötig. Bestätigte Versionen pro Sitzung merken und nur bei Fehler wieder freigeben:
  ```js
  const sent = new Set();
  // in pushMark/pushVol vor eventKey:
  if (sent.has(version)) return;
  queue(k, () => db.collection('flown').doc(key).set(value).then(() => { sent.add(version); }), version);
  ```

**F2 – Browser-Sync-Tests passen nicht mehr zum neuen Code (sicher)**
- `v2/tests/make_sync_tests.py:94` erwartet `['flown/L002']`, Zeile 101 erwartet `['flown/L010']`.
- Der neue Code schreibt `flown/f_L002_2000_<uuid>`. In Szenario 2 kommt zusätzlich `resets/p4000_v4000` dazu, weil der `meta/reset`-Handler den alten Reset übernimmt (`v2/app.js:230-234`).
- Die gebauten HTML-Dateien enthalten den neuen Code noch nicht. Nach dem nächsten Build zeigen Szenario 1 und 2 deshalb FAIL. Das README nennt diese Seiten als Prüfschritt (`v2/README.md:50`, `55`).
- **Abhilfe:** hochgeladene Legs über `__store.flown[…].legId` vergleichen, den Reset-Schreibzugriff in Szenario 2 ausdrücklich erwarten, und ein Szenario „verspäteter älterer Schreibzugriff, frisches Gerät“ ergänzen.

**F3 – Offene Sim-Prüfung für das Ausweichziel FMZJ fehlt in der Kapitelvorbereitung**
- Die Kapitel-Checkliste berücksichtigt nur Start- und Zielflughäfen der Legs (`v2/app.js:938-951`).
- FMZJ ist nirgends Start oder Ziel. Es ist nur das Ausweichziel des Ausflugs TF (`v2/tour-v2.json:19084-19087`: FMCZ → FMZJ). Der Datenvertrag nennt FMZJ ausdrücklich als unbestätigt.
- Folge: Die Prüfung erscheint nur in der globalen Liste (`v2/app.js:958`). Sie fehlt im Kapitel mit X-TF-1/2, auf jeder Airport-Karte und beim Hinweis „Ausweichziel …“ (`v2/app.js:426`).
- **Abhilfe:** Für H160-Legs `XC[l.x].fallback.anchor/target` nur in die Sim-Prüfliste des Kapitels aufnehmen, als „Ausweichziel“ gekennzeichnet, nicht in die Downloads.

**F4 – `simCheck.sources` wird nirgends angezeigt**
- `simCheckNote` (`v2/app.js:470-473`) zeigt nur `note`. Der Vertrag sieht `sources:[url]` vor.
- Folge: Die Belege für die offenen Prüfungen (ZMCK, ZDM, FMZJ) sind in der Seite nicht erreichbar.
- **Abhilfe:** Quellen als `<a href="${esc(u)}" target="_blank" rel="noopener">Quelle n ↗</a>` anhängen, gleich in Karte, Kapitel und globaler Liste.

Bei der Szenerie-Oberfläche habe ich sonst nichts Kritisches gefunden. Alle neuen Felder laufen durch `esc`. Kandidaten stehen weder in der Download-Checkliste noch im Freeware-Filter. `stdok` erscheint als „Angebot recherchiert“ mit ehrlichem Begleittext, und `alt` wird nicht zur Pflicht.

## Optionale Verbesserungen

1. **Installationshinweise bei weiteren Status:** Abhängigkeiten und `installNote` fehlen bei `owned`, `hand` und `stdok` auf der Karte (frühe Returns, `v2/app.js:476-481`) und bei `hand`/`stdok` in der Checkliste (`v2/app.js:944`). Die geplanten Fälle (RJOO, DNMM, VOCI, ELLX, YPKG) sind Freeware, heute geht also nichts verloren. Entweder überall anzeigen oder den Vertrag entsprechend einschränken.
2. **`alt` beschriften:** `alt` steht unbeschriftet direkt vor den jetzt beschrifteten Abhängigkeiten (`v2/app.js:485`, `926`, `929`). „Alternative:“ davorsetzen. Vorher muss RJOOs `alt` „Fix (Daikichi)“ (`v2/content.json:1641-1644`) in die Abhängigkeiten wandern, denn das ist ein Pflicht-Fix (Datenlauf).
3. **Hauptbadge und CSV:** Beide nehmen `items[0]` (`v2/app.js:344`, `1118`). `candidate` muss im Build hinter `stdok`/`unrated` einsortiert werden. Im geprüften Stand kennt `v2/build_v2.py:193` diesen Status noch nicht, das bitte mit dem Opus-Lauf abstimmen.
4. **UI-Test:** `v2/tests/check_scenery_ui.cjs:43` prüft einen Text, den `renderScn` nie enthielt. Die Umbenennung ist dadurch ungeschützt. Besser auf „Angebot recherchiert“ bzw. das Fehlen von „Standard bewusst empfohlen“ prüfen und Quellen, Ausweichziel sowie globale Liste mit abdecken.
5. **Formulierung:** In `v2/app.js:970` „je Airport geprüft“ zu „je Airport recherchiert“ ändern.
6. **Zählung:** „N zu besorgen“ (`v2/app.js:950-952`) zählt Pflicht-Abhängigkeiten nicht mit.
7. **Karte:** Sie zeigt nur die ersten drei Items (`v2/app.js:497`). Kandidaten oder Optionen samt Abhängigkeiten können dadurch wegfallen.
8. **Absicherung:** `deps.filter(d => d && d.product)` in `v2/app.js:466`, damit ein kaputter Eintrag nicht das ganze Panel abbricht.
9. **Wachstum:** Die neuen Dokumente wachsen unbegrenzt. Später könnte man überholte Dokumente und solche vor dem letzten Reset löschen.

## Verbleibende Grenzen (kein Fehler, nur dokumentieren)

- **Alte HTML-Stände:** Sie ignorieren die neuen Dokumente und die Reset-Collection (Filter `legIdx.has(d.id)`, `astra-changes.patch:150`). Sie zeigen dann veraltete Stände, zerstören aber nichts. Das steht schon im README (`v2/README.md:40`).
- **Uhrzeit als Maßstab:** Eine Änderung auf einem Gerät, das einen Reset noch nicht empfangen hat, verliert, wenn ihr Zeitstempel nicht nach dem Reset liegt. `doReset` hebt den Reset-Zeitpunkt auf den höchsten beobachteten Zeitstempel (`v2/app.js:1054`, `1058`). Nach einem Gerät mit vorgehender Uhr gilt das also länger.
- **Volanta-Reset und Debriefings:** Der Reset berücksichtigt `debriefTs` nicht (`v2/app.js:301-304`). Ein Debriefing mit `volantaAt` in der Zukunft überlebt ihn.
- **Beim Schließen noch offene Schreibzugriffe:** Sie bleiben bis zum nächsten Öffnen desselben Browsers nur lokal.
- **Vollständige Snapshots:** Das Zusammenführen setzt voraus, dass jeder Snapshot alle Dokumente enthält. Das DB-Verhalten ist im Repo nicht dokumentiert.

## Fazit

Im Sync-Kern gibt es keinen blockierenden Fehler, und die Frage nach dem geschlossenen Gerät ist gelöst. Vor der Abnahme:
- F1 bis F4 beheben (jeweils kleine Änderungen).
- `astra-changes.patch` neu erzeugen.
- Danach `check_sync.cjs`, `check_scenery_ui.cjs` und die neu gebauten Browserseiten erneut laufen lassen.