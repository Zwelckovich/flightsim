## Nachprüfung F1–F4

Alle vier Findings sind im Code behoben. Die fünf Dateien kann ich freigeben. Offen ist nur, die Browser-Testseiten nach dem nächsten Build wirklich laufen zu lassen.

Ich habe nur gelesen und keine Tests ausgeführt. Die SHA-256-Werte konnte ich mit Lesetools nicht nachrechnen. Geprüft habe ich den aktuellen Inhalt; die Zeilennummern waren am Anfang und am Ende der Prüfung gleich. Der Patch enthält die neuen Stellen.

**F1 – behoben**
- `queue` (`v2/app.js:119-141`) schaut zuerst nach bestätigten, dann nach noch laufenden Uploads.
- Als Version zählt der ganze Inhalt (`v2/app.js:161`, `v2/app.js:169`) bzw. der Reset-Schlüssel (`v2/app.js:176`), nicht die Zufalls-ID. Ein Snapshot ohne das Dokument löst also keinen neuen Upload aus, egal ob der Upload noch läuft oder schon bestätigt ist.
- Als bestätigt gilt ein Upload nur, wenn `set` erfolgreich war (`.then` vor `.catch`). Ein fehlgeschlagener Upload bleibt unbestätigt, und der nächste Snapshot sendet ihn erneut.
- Eine echte neue Änderung wird nie verschluckt, weil `stamp` den Zeitstempel immer erhöht.
- Die Liste der laufenden Uploads wird erst gelöscht, wenn sie leer ist. Dabei geht nichts verloren.
- `check_sync.cjs:212-228` deckt genau diese beiden Abläufe ab.
- Was bleibt, stört das Zusammenführen nicht: Fehlt ein Dokument im Snapshot, entsteht höchstens ein inhaltsgleiches Duplikat pro Version und Seitenaufruf. Dasselbe passiert, wenn ein Upload gespeichert wurde, die Bestätigung aber verloren ging.

**F2 – im Code behoben, im Browser noch nicht gelaufen**
- `uploadedLegs()` liest `legId` aus dem Dokument (`make_sync_tests.py:56`). Der Reset-Upload in Szenario 2 wird über den `flown/`-Filter ausgeblendet und stört nicht mehr.
- Szenario 6 prüft einen verspäteten älteren Eintrag auf einem neuen Gerät, Szenario 7 unabhängige Resets.
- **Aber:** `Volanta-Worldtour-V2.html` enthält noch keinen neuen Sync-Code (weder `confirmedWrites` noch `eventKey`). Die Testseiten würden also den alten Code prüfen. Nach dem Build neu erzeugen und öffnen.

**F3 – behoben**
- Kapitel 19 enthält X-TF-1/2 mit dem Ausweichflug FMCZ → FMZJ.
- FMZJ erscheint im Kapitel als „FMZJ · Ausweichziel“ (`v2/app.js:952-972`), aber nicht bei den Downloads oder in der Vorbereitung.
- FMCZ ist über L268 ein normales Ziel und wird zu Recht nicht als Ausweichziel beschriftet.
- Die Ausflugskarte zeigt den Hinweis auch (`v2/app.js:522`, `v2/app.js:530`).
- **Einschränkung:** In `tour-v2.json` hat FMZJ noch kein `simCheck`; der Test setzt es künstlich (`check_scenery_ui.cjs:39`). Sichtbar wird der Hinweis erst mit dem Datenlauf.

**F4 – behoben**
- `simCheckNote` (`v2/app.js:479-484`) hängt „Quelle n ↗“ überall an: Karte, Kapitel, Gesamtliste und Ausflug.
- `esc` verhindert, dass eine URL aus dem Link-Attribut ausbricht. Ob die Adresse mit `https:` beginnt, wird wie bei allen anderen Links nicht geprüft. Bei Daten aus dem eigenen Repo ist das vertretbar.
- Der Test prüft nur den Teil ab „Download-Checkliste pro Kapitel“. Quellen und FMZJ werden also wirklich im Kapitel geprüft.

**Kleine UI-Korrekturen – vorhanden**
Karten zeigen alle Items, Installationshinweise stehen bei owned/hand/stdok und in der Vorbereitung, „Alternative:“ und „recherchiert“ sind da, fehlerhafte Abhängigkeiten werden aussortiert.

Optional, blockiert nichts:
- „N Hauptpakete · M zusätzliche Empfehlungen“ klingt nach N+M Paketen, M ist aber Teil von N. Besser: „davon M zu besorgen“.
- `renderXcards` prüft nur, ob es ein `simCheck` gibt, nicht ob es noch offen ist. Ist FMZJ später bestätigt, bleibt „Ausweichziel FMZJ“ als leere Überschrift stehen.

**Freigabe: ja**, für die fünf Dateien in diesem Stand. Danach noch zu tun, wie schon festgehalten:
- nach dem Datenlauf bauen
- Browser-Testseiten neu erzeugen und prüfen
- echte Cloud und Layout prüfen