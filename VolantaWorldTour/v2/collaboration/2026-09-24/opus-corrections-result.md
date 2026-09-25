# Opus – Korrekturrunde nach Astras Review (24.09.2026)

Geändert: `v2/content.json`, `v2/integrate_research.py` (nur `REASON` und Kommentar).
Nicht angefasst: `check_scenery_data.py` (kein Bedarf, siehe unten), App-Code, erzeugte Ausgaben, Archiv `research-2026-09-24.json`,
Freeware-Auswahl, Status und Bewertungen. Nichts heruntergeladen, keine Sim-Dateien berührt.
**Wieder kein Shell-Werkzeug:** Build und Tests nicht ausgeführt, nur statisch geprüft.

## Änderungen

1. **SCGC:** `dependencies` = Winter Asset Pack (Usatix, `/addon/23158/`), `required: false`. Note: auf der Seite „Required“, laut
   Beschreibung nur für die Pistenraupen; kosmetische Ergänzung, ohne sie fehlen die Raupen, die Bahn liefert das Hauptpaket.
   Hauptpaket bleibt `required: true`.
2. **VQPR:** `dependencies` = Windy Things (trfsto, `/addon/14024/`), `required: false`. Note erklärt den Unterschied: auf der Seite „Required“,
   laut Beschreibung nur für die Flaggen. Hauptpaket bleibt `required: true`.
3. **FHSH `installNote`:** Quelle nachgelesen (`/addon/21642/`): Die Datei steckt im einzigen Download (Auto-Install v2.1.3), Autor: „Just delete
   the file 'navdata-fhsh.bgl' if you have subscribed 3rd party global navdata from vendors like Navigraph.“ Formuliert als „aus dem Paket
   entfernen“. „Ohne solche Navdaten bleibt sie drin“ beschreibt die Standardinstallation; eine eigene Aussage des Autors dazu gibt es nicht,
   deshalb steht dort kein „laut Autor“.
4. **EGYP__fw `why`** und identisch `REASON["EGYP"]`: „… Dass sie in MSFS 2024 läuft, beruht auf einem Nutzerbericht, den der Autor begrüßt;
   getestet hat er v1.9.1 laut Changelog aber nur in MSFS 2020 (natives 2024-Update noch geplant).“ Status/Bewertung unverändert.
5. **HAAB__fw `why`** und identisch `REASON["HAAB"]`: bisheriger Text vollständig erhalten (Nutzerberichte 2025/2026, Taxiway-Versatz), ergänzt um
   „Der Autor nennt nur MSFS 2020: … in 2024 nie getestet; auf Nachfrage schreibt er, sie laufe nur in 2020. Dass sie in MSFS 2024 läuft, ist
   damit nicht vom Autor bestätigt – die Nutzerberichte widersprechen seiner Aussage.“ Beleg: Meine Erstlauf-Notiz stammte aus einer
   Modell-Zusammenfassung, deshalb habe ich nur diese Quelle erneut gelesen. Autor: „The scenery is for the 2020. Never tested in 2024.“ und
   „No. It works only in 2020. …“; dagegen DROGE (vor ca. 6 Monaten): „works just fine“ in 2024, CaptainLars (vor ca. 1 Jahr): Taxiways versetzt.
6. **EKVG Briefing:** „Freeware-Pflicht: superspud.“ → „Freeware-Empfehlung: superspud.“

## Statische Prüfung

- Den Soll-Text von EGYP und HAAB per Regex gesucht: in `content.json` einmal, in den zusammengesetzten `REASON`-Strings (mehrzeilig) einmal.
  Beide Stellen sind zeichengleich, einschließlich „–“ und „;“. Beide enden auf Punkt, `sentence()` ändert also nichts.
- Neue Blöcke: Nachbarschlüssel, JSON-Kommas und CRLF per Mehrzeilensuche geprüft. Nur Felder aus `DEP_KEYS`, https, `required` als bool.
- Zählung jetzt 29 `dependencies`-Listen und 26 `installNote` (vorher 27 bzw. 25).
- `check_scenery_data.py` bleibt unverändert: Schritt 3 vergleicht die Integration bereits Eintrag für Eintrag mit `content.json`. Ein fehlendes
  oder abweichendes `REASON` fiele als „Integration weicht ab: scenery.EGYP__fw/HAAB__fw“ auf. SCGC, VQPR und FHSH sind handgepflegt (nicht in
  der Recherche) und werden vom Integrator nicht berührt.

## Hinweise für Astra

- **HAAB-Tag:** Beim erneuten Abruf meldete das Werkzeug neben „MSFS 2020“ auch „MSFS 2024“ als Umschalt-Reiter am Download-Knopf. Unklar ist, ob
  das eine Add-on-Kennzeichnung ist oder der Seiten-Umschalter. „nur als MSFS 2020 getaggt“ aus der Recherche steht deshalb unverändert.
  Bitte beim Blick auf die Seite gegenprüfen.
- **FHSH:** Laut Abruf erwähnt der Autor außerdem ein bekanntes „double runway“-Problem mit Video- und Forenlink. Nicht übernommen: nicht
  beauftragt, Zusammenhang nicht geprüft.
