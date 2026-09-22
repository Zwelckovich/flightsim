# Review des Fenix A320 Flow

Stand des Reviews: 22.09.2026. Geprüfte Datei: `M:\flightsim\docs\flows\fenix_a320\Fenix_A320_Flow.html`.

SHA256 der geprüften HTML: `7A5B022DB07B9BFBB972EA8DC944C4783202014D2D6EE3719433F7D7F50B3941`.

Die Datei wurde nicht verändert. Die Bewertung betrifft eine Simulatorhilfe. Der Code enthält 50 Bereiche: 23 Normal Flows, 13 Special Procedures, acht Checklisten und sechs Referenzseiten, insgesamt 605 abhakbare Zeilen.

**Einschätzung:** Die Trennung von Flow, Checkliste und Referenz sowie die aufklappbaren Erläuterungen sind eine gute Grundlage. Vor allem die Zuordnung von Datenfeldern, einige fachliche Verkürzungen und die Quellenkennzeichnung sollten vor einer weiteren Erweiterung korrigiert werden. Der pauschale Hinweis „Verified against …“ vermittelt derzeit mehr Sicherheit, als die Belege hergeben.

**Prüfumfang:** HTML und JavaScript vollständig gelesen, ursprüngliche Markdown-Datei verglichen, ausgewählte Grafiken angesehen, gezielte JavaScript-Proben durchgeführt und öffentliche Hersteller-/Fachquellen abgeglichen. Anschließend wurden unter `M:\Downloads\docs` 41 PDFs mit insgesamt 513 Seiten inventarisiert, ihre vorhandenen Texte extrahiert und die relevanten Verfahrensseiten gezielt verglichen. Engine Failure, Touch-and-go, Overweight, QRH-Titel/Overweight, Memory Items und Cruise-Fuel-Check wurden auch als gerenderte Seiten geprüft. Dies ist keine fachliche Vollvalidierung aller Quellseiten. Kein Flug im Fenix. Die Online-Fassung der Hauptquelle trägt inzwischen 20.03.2026; die konkret genannte Fassung vom 15.07.2024 fehlt weiterhin.

**Nachfolgende Umsetzung:** Auf Wunsch wurde eine getrennte V2 erstellt. Dieser Bericht beschreibt weiterhin die unveränderte V1; umgesetzte Änderungen und verbleibende Gültigkeitsfragen stehen in der V2-Dokumentation. Die V2 wurde zusätzlich im Browser geprüft.

## Zuerst korrigieren

### 1. Freigegebene FCU-Höhe und Acceleration Altitude teilen dasselbe Eingabefeld

**Befund: eindeutig im Code.** In [Zeile 419](M:/flightsim/docs/flows/fenix_a320/Fenix_A320_Flow.html:419) verwendet „FCU — Initial CLB ALT“ `{{acc}}`. Dasselbe Feld steht bei „PERF TO — THR RED / ACC“ in [Zeile 482](M:/flightsim/docs/flows/fenix_a320/Fenix_A320_Flow.html:482). Die Felddefinition enthält keine eigenständige freigegebene FCU-Höhe.

Beispiel: Bei einer freigegebenen Anfangshöhe von 5.000 ft und einer Acceleration Altitude von 3.000 ft kann die HTML nicht beide Werte korrekt darstellen. Die Verknüpfung wurde mit dem tatsächlichen Datensatz nachvollzogen.

**Änderung:** `initialClearedAlt`, `thrRedAlt`, `accAlt`, gegebenenfalls `eoAccAlt` und `missedApproachAlt` getrennt führen. Jede Höhenangabe mit Referenz versehen: Höhe über Flugplatz, QNH-Höhe oder Flight Level. Keine automatische Gleichsetzung zwischen Freigabe und Performance-Höhen.

Vorgeschlagene Zeile: `FCU — INITIAL CLEARED ALT … SET {{initialClearedAlt}} / CROSS-CHECK CLEARANCE`.

### 2. Den Ersatz-CG von 25.0 entfernen

**Befund: fachlich ungeeigneter Standardwert.** [Zeile 352](M:/flightsim/docs/flows/fenix_a320/Fenix_A320_Flow.html:352) empfiehlt 25.0, wenn kein CG angegeben ist. Dadurch kann eine fehlende Information wie ein bestätigter Beladungswert aussehen.

**Änderung:** Tatsächliches ZFW/ZFWCG aus dem finalen Loadsheet übernehmen und TOW/Takeoff-CG für die zugehörige Trim-/Performance-Prüfung eindeutig unterscheiden. Ohne Daten bleibt der Schritt offen. Fenix erläutert ausdrücklich die getrennten Loadsheet-Felder MACZFW und MACTOW. [Fenix: ACARS Overview](https://support.fenixsim.com/hc/en-us/articles/12374778266127-ACARS-Overview).

Vorgeschlagene Zeile: `FINAL LOADSHEET … CHECK; ZFW/ZFWCG ENTER; TAKEOFF DATA CROSS-CHECK`. Kein frei gewählter Ersatzwert.

### 3. Den Fuel Check auf einen gemeinsamen Bezugspunkt bringen

**Befund: missverständliche bzw. bei wörtlicher Ausführung falsche Vergleichsanweisung.** [Zeile 707](M:/flightsim/docs/flows/fenix_a320/Fenix_A320_Flow.html:707) vergleicht die Prognose für den nächsten Wegpunkt mit „actual“, ohne festzulegen, ob der Wegpunkt bereits erreicht wurde. Aktueller Tankinhalt und prognostizierter Tankinhalt an einem zukünftigen Punkt sind nicht derselbe Zustand.

**Änderung:** Zwei Kontrollen unterscheiden: Plausibilität von FOB plus Fuel Used gegenüber dem Ausgangsbestand und Plan-/Ist-Abgleich am gleichen Wegpunkt. Den OFP-/SimBrief-Plan als unabhängigen Vergleich erhalten; eine fortgeschriebene FMS-Prognose ersetzt ihn nicht. Airbus beschreibt diese unterschiedlichen Kontrollen ausdrücklich. [Airbus: Fuel Monitoring on A320 Family Aircraft](https://safetyfirst.airbus.com/fuel-monitoring-on-a320-family-aircraft/?airbus-iframe=true&airbus-post=2147).

Vorschlag für die Kurzzeile: `FUEL CHECK … FOB + FU / INITIAL FOB; ACTUAL vs OFP AT SAME POSITION`. Einzelheiten und Toleranzen in die belegte Erläuterung.

**Originalabgleich:** Auch [SOP Cruise](<M:/Downloads/docs/A320/SOP/6_A320-Cruise.pdf>), PDF-Seite 7, zeigt explizit FOB + FU gegenüber dem Abflugbestand und den Vergleich mit dem Computerised Flight Plan.

### 4. Die Engine-out-Kurzfassung verliert eine wichtige Bedingung aus dem eigenen Briefing

**Befund: interner Widerspruch.** In [Zeile 519](M:/flightsim/docs/flows/fenix_a320/Fenix_A320_Flow.html:519) steht ausdrücklich, dass auch bei noch nicht gesichertem Triebwerk die maximale Engine-out Acceleration Altitude berücksichtigt werden muss. Die später verwendete Spezialkarte sagt in [Zeile 943](M:/flightsim/docs/flows/fenix_a320/Fenix_A320_Flow.html:943) dagegen uneingeschränkt „only after the engine is secured“.

**Änderung:** Eine gemeinsame, belegte Datenquelle für Briefing und Spezialkarte verwenden. Den Zusammenhang zwischen Triebwerkszustand, festgelegter Beschleunigungshöhe und zeitlicher Schubbegrenzung konsistent darstellen. Keine universelle neue Höhe einsetzen. Die Grafik nennt außerdem pauschale Bedingungen zur Flaschenentladung; diese sollten nicht ohne Prüfung des tatsächlich passenden Verfahrens als allgemeine Fenix-Anweisung erscheinen.

### 5. FSLabs-Unterlagen und Leistungswerte brauchen eine sichtbare Gültigkeitsangabe

**Befund: Herkunftslücke nachweisbar; einzelne Zahlen damit nicht automatisch widerlegt.** Die eingebettete Engine-out-Grafik bei [Zeile 931](M:/flightsim/docs/flows/fenix_a320/Fenix_A320_Flow.html:931) nennt im Bild ausdrücklich den FSLabs A320-X als vorgesehenen Einsatz. Die Bildunterschrift nennt lediglich eine Simulator-Unterlage. Bei der Overweight-Tabelle in [Zeile 1096](M:/flightsim/docs/flows/fenix_a320/Fenix_A320_Flow.html:1096) fehlen in der Darstellung identifizierbare Flugzeug-/Triebwerksausführung und Dokumentrevision.

**Änderung:** Für jede solche Grafik und Tabelle Herkunft, Datum, Modell, Triebwerk und Gültigkeit erfassen. Ohne passenden Nachweis als „Hintergrundmaterial — Übertragbarkeit auf Fenix offen“ markieren und nicht als entscheidende Performance-Tabelle anbieten. Das betrifft ebenso den aus dem Engine-out-Kontext herausgelösten allgemeinen Eintrag „Max TOGA thrust duration: 10 min“ in [Zeile 1319](M:/flightsim/docs/flows/fenix_a320/Fenix_A320_Flow.html:1319). Die fehlende Kontextbegrenzung ist hier der Befund; ein Ersatzlimit wird in diesem Review nicht behauptet.

**Originalabgleich:** Das [gelieferte QRH](<M:/Downloads/docs/A320/313562828-QRH-A320.pdf>) ist für Vueling EC-MLE, MSN 7109, A320-232, Ausgabe 22.03.2016. Die Musterzuordnung A320-232 zu IAE V2527-A5 ist im [EASA-TCDS](https://www.easa.europa.eu/en/downloads/16507/en) bestätigt. Auf PDF-Seite 114 / 80.07A liefert es eine andere Overweight-Tabelle als [das einseitige Blatt](<M:/Downloads/docs/A320/Overweight%20Landing.pdf>): etwa bei OAT <10 °C und 4000 ft Platzhöhe 80 t gegenüber 83 t. Das ist ein konkreter Beleg unterschiedlicher Datenstände bzw. Gültigkeiten; keine der beiden Tabellen ist dadurch als passende CFM-Sharklet-Tabelle bestätigt.

### 6. Taxi-Grenze und Bremstechnik widersprechen einander

**Befund: eindeutiger Textwiderspruch.** [Zeile 595](M:/flightsim/docs/flows/fenix_a320/Fenix_A320_Flow.html:595) nennt 20 kt auf geraden Taxiways und direkt anschließend eine Beschleunigung auf 30 kt. Die Referenztabelle wiederholt beides in [Zeile 1303](M:/flightsim/docs/flows/fenix_a320/Fenix_A320_Flow.html:1303).

**Änderung:** Eine einheitliche, situationsabhängige Taxi-Regel festlegen. Die Technik der selteneren Bremsbetätigung darf die dafür gewählte Geschwindigkeitsgrenze nicht überschreiben. Im Text klar zwischen Grenze, empfohlenem Ziel und Technik unterscheiden. Dieses Review setzt bewusst keine neue universelle Taxigeschwindigkeit fest.

### 7. „Ein grünes Dreieck“ um „pro Fahrwerksbein“ ergänzen

**Befund: eine wesentliche Präzisierung fehlt.** [Zeile 787](M:/flightsim/docs/flows/fenix_a320/Fenix_A320_Flow.html:787) lässt sich so lesen, als reiche ein einzelnes grünes Dreieck für das gesamte Fahrwerk. Airbus beschreibt die Bestätigung mit mindestens einem grünen Dreieck **an jedem Fahrwerksbein** auf der WHEEL-Seite. [Airbus Safety First, Ausgabe 10, Landing-Gear-Indications, gedruckte Seite 17](https://safetyfirst.airbus.com/app/themes/mh_newsdesk/pdf/safety_first_10.pdf).

**Änderung:** Die Kontrolle für Nose, Left Main und Right Main unmissverständlich formulieren; Anzeigen verschiedener Darstellungen nicht zu einer pauschalen „irgendein Grün reicht“-Regel verkürzen.

### 8. Stabile Item-IDs vor weiteren Inhaltsänderungen einführen

**Befund: technisch reproduziert.** [Zeile 1523](M:/flightsim/docs/flows/fenix_a320/Fenix_A320_Flow.html:1523) speichert Häkchen als Phasen-ID plus Array-Index. Im Test gehörte `n1:12` zunächst zum Batterie-Spannungscheck. Nach dem Einfügen einer Zeile an dieser Stelle gehört derselbe gespeicherte Schlüssel zur neuen, noch nicht erledigten Zeile.

**Änderung:** Dauerhafte IDs wie `prelim.battery.voltage` verwenden. Dazu eine Schema-/Dokumentversion und eine bewusste Migration bestehender Häkchen. Ein unbekannter Versionsstand sollte nicht stillschweigend auf neue Schritte übertragen werden.

## Fachliche Klarheit und Bedienung verbessern

### 9. Transponder-Erklärung präzisieren

[Zeile 687](M:/flightsim/docs/flows/fenix_a320/Fenix_A320_Flow.html:687) verkürzt eine spezielle Aussage über übermittelte Baro-/Selected-Altitude-Daten zu „transponder … based on the last selected QNH“. Das kann mit der eigentlichen Druckhöhenmeldung verwechselt werden. Die gefundene Fassung der verwendeten Quelle trennt diese Fälle auf Seite 28 selbst; EUROCONTROL unterscheidet Barometric Pressure Altitude, Barometric Pressure Setting und Selected Altitude ebenfalls ausdrücklich. [EUROCONTROL DAP/ADD Handbook](https://www.eurocontrol.int/publication/dap-add-handbook).

**Vorschlag:** Im Normalflow nur STD setzen und kreuzprüfen. Die Erläuterung bei Bedarf als genau abgegrenzten Avionikhinweis führen. Nicht einfach alle Mode-S-Daten mit der Druckhöhenmeldung gleichsetzen.

### 10. Die pauschalen 350 NM nicht als Reichweite darstellen

[Zeile 705](M:/flightsim/docs/flows/fenix_a320/Fenix_A320_Flow.html:705) und [Zeile 1390](M:/flightsim/docs/flows/fenix_a320/Fenix_A320_Flow.html:1390) nennen eine konstante Single-engine-Reichweite. Ohne Zeitbezug, Masse, verfügbare Treibstoffmenge, Höhe und Randbedingungen ist das keine brauchbare allgemeine Reichweitenregel.

**Vorschlag:** Den Zahlenwert aus der allgemeinen Referenz entfernen, bis der genaue Kontext geklärt ist. Stattdessen auf die flugspezifische Diversion-/ETP-Betrachtung und die passende Performance-Berechnung verweisen. Nicht ungeprüft zu einer vermeintlichen Ein-Stunden-Regel umdeuten.

### 11. CFM/IAE und bedingte Schritte tatsächlich auswählbar machen

Die CFM-Startschwellen stehen in [Zeilen ab 555](M:/flightsim/docs/flows/fenix_a320/Fenix_A320_Flow.html:555) in den sichtbaren Handlungszeilen; ihre eingeschränkte Gültigkeit für IAE wird erst in der Erläuterung erkennbar. Auch beide Triebwerks-Idle-Checks, beide Seitenwind-Startvarianten und mehrere alternative Verfahren zählen im Fortschritt jeweils als zu erledigen.

**Vorschlag:** Ein Flugprofil mit Triebwerk, Startkonfiguration, Packs, relevanten Wetterbedingungen und Anflugart. Alternative Zweige ausblenden oder ausdrücklich „nicht zutreffend“ erlauben. CFM-/IAE-Daten dort kennzeichnen, wo man die Zeile liest. Unsicher belegte IAE-Zahlen nicht allein durch einen sichtbaren Check-Haken bestätigen lassen.

### 12. Sonderfall „Glide interception from above“ aus dem normalen Capture-Schritt lösen

[Zeile 775](M:/flightsim/docs/flows/fenix_a320/Fenix_A320_Flow.html:775) platziert die Anleitung zum Einfangen von oben in der Erläuterung des normalen LOC/GS-Capture-Checks. Damit wird ein besonderer Korrekturfall nicht deutlich genug vom geplanten Einfangen von unten getrennt.

**Vorschlag:** Eigene bedingte Karte mit Aktivierungsvoraussetzungen und Verweis auf das passende Verfahren. Der Normalflow sollte an dieser Stelle nur erwartete Armed-/Capture-Modi und die dazugehörige Überwachung beschreiben.

### 13. Die Quellenkennzeichnung vom Änderungsmarker trennen

`Δ`, `+` und `§` beantworten andere Fragen als „belegt“, „Fenix-passend“ und „Operator-SOP“. Ein unverändert übernommener USER-Schritt ist nicht automatisch geprüft; ein FCOM-Badge mit lediglich mittelbarer Referenz ist kein direkter FCOM-Abgleich. Der Footer in [Zeile 1966](M:/flightsim/docs/flows/fenix_a320/Fenix_A320_Flow.html:1966) ist deshalb zu pauschal.

**Vorschlag:** Pro fachlich relevanter Zeile `sourceId`, Dokumenttitel, Revision, Seite/Abschnitt, Anwendbarkeit und Prüfstatus. Originaldateien oder zulässige lokale Quellenkopien katalogisieren. Den Stand der [online verfügbaren Hauptquelle](https://www.theairlinepilots.com/forumarchive/a320/a320-normal-procedures.pdf) nicht stillschweigend als die 2024 verwendete Fassung behandeln. Eine angemessene Formulierung wäre „Compiled from listed sources; applicability and validation shown per item“.

### 14. „Neuer Flug“ von „Häkchen zurücksetzen“ trennen

[Zeile 1918](M:/flightsim/docs/flows/fenix_a320/Fenix_A320_Flow.html:1918) lässt V-Speeds, FLEX, Trim, QNH und Höhen ausdrücklich stehen. Das ist angekündigtes Verhalten, kein versteckter Löschfehler. Für den nächsten Flug können die alten Zahlen aber weiterhin wie bestätigte aktuelle Werte aussehen.

**Vorschlag:** „Neuer Flug“ löscht oder entwertet die flugspezifischen Werte standardmäßig. „Häkchen zurücksetzen, Werte behalten“ bleibt als zweite Funktion. Flugkennung/Datum und ein Status „übernommen — erneut bestätigen“ machen bewusst wiederverwendete Daten sichtbar. QNH für Abflug und Ankunft sowie Takeoff- und Go-around-Daten getrennt behandeln.

### 15. Die Suche durchsucht gerade die wichtigen Erläuterungen nicht

**Befund: reproduziert.** [Zeile 1878](M:/flightsim/docs/flows/fenix_a320/Fenix_A320_Flow.html:1878) berücksichtigt bei Schritten nur Titel und Kurzaktion, dazu Phasentitel. Tabellen, Hinweise, Warnungen und Detailtexte fehlen. Die Suche nach `tailstrike` und `350` liefert jeweils null Treffer, obwohl beide Inhalte enthalten sind; `AP Disconnect` funktioniert.

**Vorschlag:** Alle Textarten indexieren und Treffer mit Fundkontext anzeigen. Für Tabellen-/Hinweistreffer das richtige Element öffnen und Details automatisch aufklappen. Das ist besonders bei einem Dokument mit 605 abhakbaren Zeilen nützlich.

### 16. Tastaturzugang und echte Checkboxen ergänzen

**Befund: im Code und teilweise reproduziert.** Die Häkchen sind klickbare `div`-Zeilen mit CSS-Kästchen, keine fokussierbaren Checkboxen ([Zeile 1627](M:/flightsim/docs/flows/fenix_a320/Fenix_A320_Flow.html:1627)). Gleichzeitig fängt [Zeile 1947](M:/flightsim/docs/flows/fenix_a320/Fenix_A320_Flow.html:1947) Tab außerhalb von Eingabefeldern ab und wechselt die Gruppe. Im Test wurde Tab auf einem Button tatsächlich abgefangen.

**Vorschlag:** Native Checkboxen oder vollständig implementierte Tastatur-/ARIA-Semantik; Tab für Fokusnavigation erhalten. Gruppenwechsel auf einen gesonderten Shortcut legen. Labels mit den Eingabefeldern verbinden und Info-Buttons aussagekräftig benennen.

### 17. Speicherfehler und Import/Export sichtbar behandeln

[Zeile 1517](M:/flightsim/docs/flows/fenix_a320/Fenix_A320_Flow.html:1517) verschluckt Speicherfehler. Die Anzeige kann dann ein gesetztes Häkchen zeigen, das nach dem Schließen weg ist. Geladene JSON-Werte werden außerdem nicht auf ihre erwartete Struktur geprüft.

**Vorschlag:** Speichern bestätigen oder einen sichtbaren Status „nur in dieser Sitzung“ anzeigen. Geladene Daten validieren, Fortschritt und Flugprofil exportierbar machen und unbekannte Versionsstände kontrolliert behandeln. Beim Kopieren von ICAO in [Zeile 1725](M:/flightsim/docs/flows/fenix_a320/Fenix_A320_Flow.html:1725) den Clipboard-Promise abwarten; das bestehende `try/catch` fängt eine asynchrone Ablehnung nicht ab.

### 18. Einen kurzen Flugmodus und einen ausführlichen Lernmodus anbieten

Die Datei enthält neben Handlungen auch Änderungshistorie, Hintergrundwissen, operatorgeprägte Regeln und Simulator-Sonderfälle. Das erklärt viel, verlängert aber den Scan während des Fluges. Mehrspaltiger Satz kann sich beim Öffnen langer Erklärungen zusätzlich neu verteilen; das ist eine aus dem CSS abgeleitete UX-Frage, kein visuell bestätigter Darstellungsfehler.

**Vorschlag:** Im Flugmodus nur passende Handlungen, Bedingungen und kurze Checks; Lernmodus mit Quellen, Hintergründen und Änderungsvergleichen. Reihenfolge und Position der Schritte im Flugmodus stabil halten. Nach dem Flow direkt zur passenden Checkliste springen und anschließend zum nächsten Flow zurückkehren. Dabei „TAXI C/L“, „LINE-UP C/L“ und die tatsächlich vorhandene „Before Takeoff“-Checkliste eindeutig verknüpfen.

### 19. Touch-and-go-Reihenfolge korrigieren

[Zeile 1081](M:/flightsim/docs/flows/fenix_a320/Fenix_A320_Flow.html:1081) stellt die 1000-ft-Aktion vor die 500-ft-Kurve. Im [Originaldiagramm](<M:/Downloads/docs/A320/FSLabs%20A320%20Touch%20and%20Go.pdf>), Seite 1, folgt die Kurve bei 500 ft vor der Aktion bei 1000 ft. Dies ist ein eindeutiger Übertragungsfehler, unabhängig von der weiteren Anwendbarkeit des Trainingsprofils.

### 20. Bedingungen beim Emergency Descent erhalten

Die Kurzzeile in [Zeile 1017](M:/flightsim/docs/flows/fenix_a320/Fenix_A320_Flow.html:1017) macht aus dem Transponder-Hinweis eine pauschale 7700-Anweisung. Das gelieferte QRH, PDF-Seite 112 / 80.05A, formuliert „CONSIDER“ mit ATC-Bedingung. Die Memory-Items-Grundstruktur dagegen stimmt mit [den Memory-Items-Notizen](<M:/Downloads/docs/A320/a320-memory-items.pdf>), Stand 02.12.2019, Seite 2, überein. Unterschied zwischen Bedingung und stets auszuführendem Schritt bewahren.

**Sinnvolle spätere Erweiterung:** Für die Worldtour wären eigene Karten für FINAL APP und NAV/FPA bzw. TRK/FPA hilfreich. Dafür liegen zwei zusätzliche Simulatorblätter und drei NPA-/RNAV-SOP-Dateien vor. Der jetzige Normalflow ist ausdrücklich als ILS-Anflug bezeichnet; die fehlenden anderen Karten sind eine Erweiterungsmöglichkeit, kein Beweis für einen falschen ILS-Ablauf.

## Was ich bewusst nicht pauschal beanstande

- Die Unterscheidung zwischen Flow und Checkliste ist sinnvoll und sollte erhalten bleiben.
- Die Darstellung mit knapper Handlungszeile und aufklappbarer Erklärung ist grundsätzlich passend; Quellenstatus und Gültigkeit müssen dabei sichtbar genug sein.
- Weniger strenge und strengere Disconnect-/Stabilisierungsvorgaben sind nicht schon deshalb Widersprüche, weil unterschiedliche Zahlen vorkommen. Dafür braucht es Verfahren, Flugzeugstandard und Operatorbezug. Die pauschale Aussage in der Datei, eine bestimmte AP-Höhe gelte für jede Non-autoland-Situation, sollte daher mit ihrer genauen Anwendbarkeit belegt werden, statt sie durch eine weitere pauschale Zahl zu ersetzen.
- TOGA kurz anzuwählen und bei nicht benötigtem TOGA-Schub anschließend CL zu verwenden ist nicht automatisch ein Fehler. Airbus beschreibt diese Energiekontrolle ausdrücklich; die Performance-Voraussetzungen müssen erhalten bleiben. [Airbus: Flying a Go-Around — Managing Energy](https://safetyfirst.airbus.com/flying-a-go-around-managing-energy/?airbus-iframe=true&airbus-post=2161).
- Die nur mittelbar belegten APU-Test-, Öl-, Triebwerksstart- und Tabellenwerte wurden nicht komplett für Fenix freigegeben. Die Dateien liegen nun vor, ihre passende Flugzeug-/Triebwerksgültigkeit ist jedoch nicht durchgängig belegt. Beispielsweise unterscheiden die Start-SOP-Folien ausdrücklich CFM und IAE, während das vollständige QRH einem einzelnen IAE-Flugzeug zugeordnet ist.

## Empfohlene Reihenfolge der Überarbeitung

1. Datenverknüpfungen, CG-Ersatzwert, Fuel Check, Engine-out-Widerspruch und eindeutig missverständliche Formulierungen korrigieren; stabile Item-IDs einführen.
2. Quellen und Varianten katalogisieren, nicht belegte Anwendbarkeit sichtbar machen und für den tatsächlich geflogenen Fenix ein konsistentes Profil festlegen.
3. Bedingte Zweige, neuen Flug, Suche, Tastaturzugang und kurzen Flugmodus ergänzen; danach typische Normal- und Sonderfälle im Simulator nachvollziehen.

Die technischen Proben verwendeten Kopien bzw. Datensätze im Speicher. Sie haben weder die geprüfte HTML noch ihre Browser-Häkchen verändert. Die JavaScript-Syntaxprüfung war erfolgreich. Zum Abschluss war das Git-Arbeitsverzeichnis unverändert.
