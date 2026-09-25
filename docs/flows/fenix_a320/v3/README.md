# Fenix A320 Flow · V3

24.09.2026 · Für den Fenix A320 CEO mit CFM56-5B und Sharklets – im Look der „Weltreise ab Weeze“ V2.

Startdatei: `../Fenix_A320_Flow_V3.html` (rund 235 KB, offline nutzbar; die Schriften kommen nur online von Google Fonts, sonst greifen Arial Narrow und Consolas).

## Was V3 ist

Die Zusammenführung von V1 (Fable) und V2 (Astra):

- **Grundlage:** V2 mit ihren stabilen Schritt-IDs und den berechtigten Korrekturen.
- **Wieder konkret:** Werte, die V2 durch „as briefed“ ersetzt hatte, stehen wieder da – mit Quelle. Das betrifft die Taxi-Technik, die AP-Mindesthöhen, die TOGA-Zeiten und die Ölmenge.
- **Behobene Fehler:**
  - Die After-Takeoff/Climb-Checkliste fehlte.
  - Die Abbruchkriterien sind jetzt nach Airbus formuliert.
  - Der Wing-Anti-Ice-Widerspruch ist aufgelöst.
- **Aufgeräumt:** Eurowings- und IAE-Inhalte sind entfernt.
- **Neu für die Weltreise:**
  - drei Anflugarten im Normal-Flow (ILS, RNAV mit FINAL APP, NPA mit TRK/FPA),
  - vier Karten: G/S von oben, Hot & High, kurze Bahn, Kälte und kontaminierte Bahn.

Jede Änderung gegenüber V2 steht mit Begründung im Reiter „Neu in V3“ (73 Einträge).

## Bedienung

- **Phasen:** Mit „← Zurück / Weiter →“, der Auswahl oder der Leiste „Gesamter Flug“ (23 Phasen in 5 Abschnitten). Tastatur: `←` `→`.
- **Schritte:** Zeile anklicken oder `Leertaste` hakt ab. `i` öffnet Details, Quelle und „Nicht zutreffend“. `N` springt zum nächsten offenen Schritt, auch in die zugehörige Checkliste.
- **Flug / Lernen:** „Flug“ zeigt knappe Zeilen und nur Warnhinweise. „Lernen“ zeigt dazu alle Erklärungen, Quellen-Badges und die Markierung, was in V2 oder V3 geändert wurde.
- **Flugdaten:** Pro Phase im Briefing links. Alle Felder stehen außerdem unter „Daten & Reset“. Werte erscheinen grün in den Schritten, Checklisten und Profilen; leere Felder als `___`.
- **Flugprofil:** Startlauf-Technik, T/O CONF, Anflugart, LDG CONF, manuelle Landung oder Autoland. Die Auswahl blendet die passenden Schritte ein und aus. Der Chip oben rechts zeigt das aktuelle Profil.
- **Checklisten:** Airbus Normal Checklist mit Strich, direkt bei der zugehörigen Phase und gesammelt im Reiter „Checklisten“. Es sind dieselben Häkchen.
- **Suche:** `Strg`+`K` oder `/`. Durchsucht Schritte, Werte, Hinweise und Quellen.
- **Dimmen:** Oben rechts, für Nachtflüge.
- **Speicher:** Lokal im Browser, getrennt je Datei-Adresse. Für ein anderes Gerät: Sicherung speichern und dort laden. „Neuer Flug“ löscht Häkchen und Flugdaten, das Profil bleibt.
- **Direktlinks:**
  - `…V3.html#n20` öffnet eine Phase,
  - `?tab=cl` öffnet einen Reiter (`all`, `spec`, `cl`, `ref`, `new`, `data`),
  - `?mode=learn` öffnet die Lernansicht.

## Pflege

Inhalte werden **nur in `flow-v3.json`** gepflegt. Danach im Ordner `docs/flows/fenix_a320` neu bauen:

```powershell
python v3/build_v3.py
```

Der Build prüft die Daten streng und bricht mit Fundstellen ab bei:

- doppelten IDs,
- unbekannten Typen, Quellen, Platzhaltern oder Profilwerten,
- defekten Checklisten-Links,
- HTML im Text (nur `**fett**` ist erlaubt),
- Eurowings- oder IAE-Resten.

| Datei | Inhalt |
|---|---|
| `flow-v3.json` | Einzige Datenquelle: Phasen, Schritte, Checklisten, Referenz, Quellen, Profil, Änderungsprotokoll |
| `template.html`, `app.css`, `app.js` | Seite, Designsprache der Weltreise, Logik und die neun Grafiken |
| `build_v3.py` | Prüft und baut die Offline-Datei |
| `migrate_from_v2.py` | Einmalige Überführung aus V2 (bereits ausgeführt; überschreibt nur mit `--force`) |

**Schritt-Felder:**

- `id`: stabil – beim Bearbeiten nicht ändern, sonst verlieren gespeicherte Häkchen ihren Bezug.
- `item`, `state`, `type`: `act` Aktion · `chk` Prüfung · `tgt` Zielwert · `cau` Vorsicht · `wrn` Warnung.
- `src`: Quelle, siehe unten.
- optional: `caution`, `detail`, `when` (Profilbedingung), `link` (Checkliste), `rev` (`v2`/`v3`).

Platzhalter wie `{{v1}}` beziehen sich auf die Flugdaten oder das Profil.

## Quellen

Jeder Schritt trägt seine Herkunft:

| Kürzel | Herkunft |
|---|---|
| FCOM · FCTM · NCL | Airbus-Standard nach bestem Wissen, nicht Zeile für Zeile gegen die Unterlagen des CFM-Sharklet-Musters geprüft |
| QRH | vorliegendes QRH (EC-MLE, A320-232/IAE, 2016), nur für Wortlaut |
| PROC | A320 Normal Procedures (TheAirlinePilots) |
| SIM | Simulator-Trainingsblätter |
| FENIX | Fenix-Bedienung |
| DEIN FLOW | aus deinem Flow von 2024 |
| TECHNIK | Zusammenfassung für die Weltreise |

Leistungswerte kommen immer aus dem Fenix-EFB. Nur für die Flugsimulation – kein Dokument für den echten Flugbetrieb.

## Geprüft

- **Build:** Datenprüfung ohne Befund, JavaScript-Syntax in Ordnung.
- **Browser:**
  - Abhaken, N/A, Zähler, Leiste und Tracks.
  - Profilzweige: ILS, RNAV, NPA sowie CONF 3/FULL.
  - Flugdaten in Schritten und Grafiken.
  - Lernansicht, Suche in Hinweisen, „Nächster offener Schritt“, Checklisten-Sprung, Tastatur.
  - Sicherung laden, einschließlich Abweisen fremder Dateien und unbekannter Einträge.
  - Neuer Flug, Reset, Dimmen.
  - Alle 40 Ansichten und alle Reiter rendern ohne Konsolenfehler.
- **Breiten:** Bei 375 px kein seitlicher Überlauf. Die Grafiken scrollen dort innerhalb ihres Screens.
- **Nicht geprüft:** Kein Testflug im Fenix.
