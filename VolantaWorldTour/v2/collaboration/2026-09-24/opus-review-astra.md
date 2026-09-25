# Unabhängiges Review von Astras V2-Änderungen

Du bist der ausdrücklich angeforderte Reviewer: Claude Opus 5.5, Max Effort. Prüfe ausschließlich lesend die Änderungen von Astra. Keine Dateien ändern und keine Unteragenten. Das Ergebnis wird automatisch an Astra zurückgegeben; der Benutzer muss nichts kopieren.

Projekt M:/flightsim/VolantaWorldTour. Lies v2/collaboration/2026-09-24/astra-changes.patch, v2/app.js sowie v2/tests/check_sync.cjs und v2/tests/check_scenery_ui.cjs. Ein zweiter Opus-Arbeitslauf bearbeitet gerade die Szeneriedaten/Build, die gehören nicht zu diesem Review.

## Auftrag und Vertrag

Der Benutzer will V2 gemeinsam fertigstellen und gegenseitige Reviews, keine neue V3. Astra behebt einen reproduzierten Cloud-Fall: Nach erfolgreicher erster Synchronisierung trifft ein verspäteter älterer unbedingter document.set von einem anderen Gerät ein. Die offenen Geräte behalten lokal neuere Daten, korrigierten vorher aber die Cloud nicht. Frische Geräte sahen den älteren Stand.

Die Änderung gleicht nun bei jedem Snapshot ab, auch Reset-Epochen. Gleichstände sind deterministisch, lokale Änderungen und Resets berücksichtigen bereits beobachtete spätere Zeitstempel. Prüfe Korrektheit, neue Uploadschleifen, Reset-Rennen und ob der Fix auch hinreichend robust ist, wenn das Gerät mit dem neuesten Stand bereits geschlossen ist. Die vorhandene Datenbankoberfläche ist window.claude.use('db') mit doc/collection/set/onSnapshot; keine Transaktionen oder bedingten Schreibzugriffe unterstellen, wenn nicht belegt. Falls wirklich erforderlich, benenne klar die Grenze der bisherigen Strategie und eine minimale kompatible Abhilfe.

Szenerie-UI: stdok wird ehrlich „Angebot recherchiert“, keine getestete Standardqualität behauptet. Neue Items mit status candidate sind kostenlose Beobachtungskandidaten, nicht Teil der empfohlenen Downloadliste. Item.dependencies ist ein Array {product,dev?,url,required:boolean,note?}; installNote freier Text. airport.simCheck={status:'unconfirmed',note,sources:[url]} wird sichtbar, auch in der Kapitelvorbereitung. Bestehendes alt bleibt eine Alternative. Prüfe esc, Verlinkungen, Statusdarstellung, praktische Informationsverluste.

Astra hat JavaScript-Syntaxcheck und elf Sync-Szenarien sowie den neuen UI-Renderingtest erfolgreich ausgeführt. Du hast keine Shelltools; bewerte Testabdeckung und tatsächlichen Code, behaupte keine eigenen Testläufe.

Liefere priorisierte, belegte Findings mit Datei/Zeile und konkretem Trigger; trenne echte Fehler von optionalen Verbesserungen. Wenn keine Findings: explizite Freigabe mit verbleibenden Grenzen. Keine pauschale Übernahme von Astras Diagnose.
