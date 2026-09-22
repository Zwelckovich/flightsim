# Fenix A320 Flow V2

22.09.2026 · Für den persönlichen Fenix A320 CEO mit CFM56-5B und Sharklets.

Startdatei: `../Fenix_A320_Flow_V2.html`. Die HTML ist vollständig offline nutzbar, einschließlich der neuen Cockpit-Illustration und der ursprünglichen Bilder. Sie benötigt weder Server noch Installation. Externe Quellenlinks benötigen Internet.

## Bedienung

- **Flugdaten:** Flugkennung, Airports, getrennte Abflug-/Ankunfts-QNH, Freigabehöhe, THR RED, ACC, EO ACC, V-Speeds, Trim, FLEX und Anflugdaten. PERF-Höhen in ft QNH; Freigabe/Go-around mit eindeutiger Höhenreferenz. Keine automatische Performance-Berechnung.
- **Flugmodus:** Kurze, stabile Liste. Nicht zutreffende Profilzweige und Originalgrafiken sind ausgeblendet. Hinweise und Details bleiben erreichbar.
- **Lernmodus:** Zusätzliche Ablaufübersichten, Originalgrafiken im Archiv und Quelleninformationen pro Schritt. Die Cockpit-Illustration ist dekorativ.
- **Bedingungen:** CFM festgelegt; Wind-Technik, Takeoff-/Landing-Konfiguration, manuelle Landung/Autoland sowie Go-around/Discontinued Approach auswählbar. Die Auswahl ersetzt keine Prüfung der Verfahrensvoraussetzungen.
- **N/A:** Mit dokumentiertem Grund aus dem Fortschritt nehmen; erneut klicken zum Aufheben.
- **Neuer Flug:** Häkchen, N/A und alle Flugdaten löschen. CFM-Profil und Ansicht bleiben erhalten; Wind-Zweig wird erneut abgefragt.
- **Alle Häkchen zurücksetzen:** Häkchen und N/A löschen, Daten behalten. Separat gibt es einen Reset nur für die aktuelle Phase.
- **Backup:** JSON exportieren oder ein V2-Backup nach Strukturprüfung importieren. Import ersetzt die aktuelle Sitzung nach Bestätigung.
- **Tastatur:** Tab bewegt den Fokus, Leertaste bedient Checkboxen. Strg+K öffnet die Suche, Alt+Links/Rechts wechselt die Phase. Escape schließt Dialoge.
- **Speicherung:** Lokal im jeweiligen Browser. Bei Speicherfehlern erscheint ein Hinweis; Backup exportieren. Wechsel zwischen Browser, Dateipfad und Serveradresse kann einen separaten Speicherbereich verwenden.

## Wesentliche Korrekturen gegenüber V1

Freigegebene FCU-Höhe und PERF-ACC sind getrennt. Ein unbekannter CG wird nicht mit 25.0 ersetzt. Fuel Checks vergleichen Werte am gleichen Bezugspunkt und berücksichtigen FOB + Fuel Used. Gear-down bestätigt jedes Fahrwerksbein. Die 20/30-kt-Taxi-Unstimmigkeit, die pauschale Single-engine-Reichweite und die allgemeine Zehn-Minuten-TOGA-Angabe wurden bereinigt. Das Touch-and-go-Profil enthält die 500-ft-Aktion vor der 1000-ft-Aktion. Beim Emergency Descent bleibt die ATC-Bedingung für 7700 erhalten.

Die Engine-out-Karte weist auf den Konflikt zwischen „only after engine secured“ und maximaler Beschleunigungshöhe hin. Beide Textstellen beschreiben jetzt denselben Zusammenhang; eine vollständige flugzeugspezifische Engine-out-Validierung ist damit nicht behauptet.

V1 nutzt teilweise FSLabs-Blätter und sekundäre Unterlagen. Das gelieferte QRH gehört zu EC-MLE, A320-232/IAE, Ausgabe März 2016. Die zwei Overweight-Tabellen unterscheiden sich. Eine passende CFM-Sharklet-Tabelle ist weiterhin nicht belegt; das alte Bild bleibt als entsprechend markiertes Lernmaterial erhalten. Der Quellenkatalog führt 41 PDFs auf; relevante Seiten wurden gezielt verglichen, nicht alle 513 Seiten fachlich freigegeben.

## Gestaltung

Alle zehn V1-Bildthemen sind aufbereitet: acht SVG-Lerntafeln und zwei strukturierte HTML-Referenzen. Neu sind Cockpit-Zonenkarte, Vergleich der Anflugtechniken, Engine-out-Steigprofil, Quick-return- und Circling-Platzrunden, Touch-and-go mit Bahnablauf sowie das Flap-Zustandsdiagramm. Visual Approach bleibt erhalten. Emergency Descent trennt Memory Items und Folgeaktionen; Overweight enthält eine gekennzeichnete historische Quellentabelle.

Jede Darstellung bietet den V1-Originalvergleich. SVGs lassen sich im Dialog vergrößern und separat speichern. Die vorhandene Cockpit-Aufnahme bleibt unverändert; es handelt sich nicht um einen neuen Fenix-Screenshot. Engine-out- und Overweight-Anwendbarkeit sind weiterhin nicht vollständig geklärt und direkt markiert. Alle Bilder sind eingebettet. Details: `GRAPHICS_REVIEW.md`.

Die dekorative Cockpit-Illustration und die vorherige Visual-Approach-Studie stammen von OpenAI Image (`IMAGE_PROMPT_V2.md`, `IMAGE_PROMPT_VISUAL_APPROACH.md`). Technische Diagramme sind kontrollierte SVGs, Tabellen und Abläufe sind HTML. Der N/A-Abbrechen-Button funktioniert auch ohne ausgefüllten Grund.

## Prüfung

JavaScript-Syntax, eindeutige stabile IDs, Höhenverknüpfung, bekannte Platzhalter, Backup-Strukturprüfung, bedingte Zweige und Volltextsuche wurden automatisiert geprüft. 50 Bereiche und 609 dauerhaft identifizierte Schritte sind enthalten; alternative Zweige zählen nicht gemeinsam zum aktiven Fortschritt. Im Browser wurden Eingaben, getrennte Werte, Häkchen nach Neuladen, Detailsuche, Profilfilter, N/A und Neustart geprüft. Die schmale Ansicht hat keinen horizontalen Überlauf; Desktop-Darstellung und Fuel-Grafik wurden angesehen. Keine Konsolenfehler in den geprüften Abläufen. Kein Testflug im Fenix.

V1 ist unverändert. Ihr SHA256 lautet `7A5B022DB07B9BFBB972EA8DC944C4783202014D2D6EE3719433F7D7F50B3941`. V2 verwendet einen eigenen Speicherbereich; alte Häkchen werden nicht stillschweigend übertragen.

## Pflege

Die V2-HTML wird aus `v2-template.html` und den gezielten Änderungen in `build-v2.cjs` erzeugt. Die unveränderte V1 dient als Ausgangsdatensatz. Ihre Prüfsumme wird vor dem Neubau geprüft, damit eine veränderte V1 keine falsche ID-Zuordnung erzeugt.

Im Ordner `v2` ausführen:

```powershell
node build-plates.cjs
node build-v2.cjs
node verify-v2.cjs
node verify-graphics.cjs
```

Der Build überschreibt ausschließlich die V2-Ausgabedatei und abgeleitete V2-Daten, niemals die V1. Änderungen deshalb in Template und Build-Skript pflegen. `REVIEW_V1.md` enthält die Befunde mit Fundstellen. Neue Schritte bekommen neue feste IDs; vorhandene IDs beim Bearbeiten und Umordnen beibehalten.
