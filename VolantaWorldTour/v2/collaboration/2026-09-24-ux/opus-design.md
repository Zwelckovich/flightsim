# Aufgabe: Design und responsive Bedienbarkeit der Worldtour verbessern

Projekt: M:\flightsim\VolantaWorldTour
Modell: Claude Opus 5.5, Max Effort. Koordinator ist Astra/Codex.

Arbeite nach M:\flightsim\cowork.md. Relevante README: v2/README.md. Keine weiteren AGENTS.md/CLAUDE.md im Projekt gefunden. Bestehende V2-Dateien sind noch untracked; niemals zurücksetzen. Baseline und Hashes unter v2/collaboration/2026-09-24-ux/baseline und baseline-manifest.json.

## Exklusive Dateizuständigkeit
Du darfst ausschließlich M:\flightsim\VolantaWorldTour\v2\app.css ändern. Astra ändert parallel template.html und app.js. Keine anderen Dateien, keine Unteragenten, kein Commit/Push, keine Recherche und keine Shell. Gib deinen Übergabebericht in der finalen Antwort aus; der Runner speichert ihn.

## Nutzerziel und beobachtete Probleme
Review und nötige Verbesserung von http://localhost:8000/ (Weltreise ab Weeze V2). Dunklen Schiefer/Cyan-Instrumentenstil beibehalten. Aktuell sehr kleine 6-9 px Pips, schwache Textkontraste, 32 px Buttons, große Karte und Navigation ganz unten. Auf kleinen Breiten können Kartenraster minmax(300/320px,1fr) überlaufen. Keine Komplettneugestaltung, keine neuen Abhängigkeiten oder Bilder. Verbessere Lesbarkeit, Fokus, Abstände, optische Hierarchie, Touchziele und Reflow bis 320px. Bestehende Ansichten/Map/Globus/Szenerie-Daten bleiben.

## Verbindlicher neuer HTML-Vertrag (Astra implementiert)
- Navigation wandert aus footer nach nav.stepbar > div.wrap > div.legnav. Die stepbar bleibt sticky oben.
- .legnav enthält in dieser Reihenfolge: button#prev.btn „← Zurück“, label.leg-picker mit span#nav-position (z.B. „Etappe 1 von 422 · A320“) und select#jump (bestehende optgroups; Beschriftung „001 · EDLV → EHAM · Amsterdam“), button#next.btn „Weiter →“, div.nav-shortcuts mit button#resume.btn „Erstes offenes Leg“ und button#find-leg.btn „Leg suchen“.
- Unterhalb von nav.stepbar als separates, NICHT sticky Element: details.route-overview.wrap > summary „Gesamte Route · 28 Kapitel“ und div#rail.rail. Standardmäßig geschlossen, Pips darin. Kapitelüberschriften werden button.chapter-link.lbl[data-go] (b Kapitel-ID, Titel, b.cnt). Pips bleiben .pip/.heli/.long/.done/.now, tragen zusätzlich sichtbare span.pip-label Nummern (001 bzw. GG-1). Vergrößere sie auf brauchbare mindestens 28px/36px Ziele; Nummern lesbar. Horizontales Scrollen der Route bleibt lokal im rail. Nur ein Pip ist Tabstop; Pfeile werden implementiert.
- main .grid ist weiterhin Briefing .prose und Karte .stage; .grid erhält tabindex=-1 für gezielten Fokus. Kein neuer hero Text.
- .book erhält id=book, bleibt nach .tracks. Schnellaktion Leg suchen springt zu Suchfeld.
- .toolbar enthält .filter-field label (span Label + input/select). Felder: Suche (#q) „Leg, ICAO, Ort oder Land“, Status (#flt), Kapitel (#chsel). button#clear-filters.btn „Filter zurücksetzen“ wird bei inaktiven Filtern hidden. Bestehender #csv.btn.small bleibt.
- div.plan-summary enthält p#planinfo[role=status] nur Trefferzahl und Auswahlkontext, p.hint „Strecke anklicken, um das Briefing zu öffnen.“ Vor Tabelle.
- Tabelle behält Struktur, Strecke enthält button.route-link[data-go] statt reinem Text. Beim Checkbox ist label.check-hit mit input und span.visually-hidden; Trefferfläche mindestens 40px, Input selbst gerne 18px.
- Leere Suche als tr.empty-row > td[colspan=8] mit strong + p, Reset bleibt in Toolbar.
- Flugzeit-Formel zieht in details.time-info > summary „Wie werden Flugzeiten geschätzt?“ > p#time-formula hinter Tabelle.
- footer enthält nur .wrap.foot mit Tastaturhinweis und credits, keine Navigation.
- a.skip-link href=#book (JS übernimmt Fokus) vor header.
- JS erhält Tabs mit roving tabindex + Pfeiltasten/Home/End; Fokusfarbe muss sichtbar sein. .tab/.seg buttons mindestens 40px Höhe, übrige Hauptbuttons 44px. Primärbutton Weiß auf aktuellem Cyan ist zu kontrastarm: passende dunkle Textfarbe oder dunkleres Cyan erwägen.

Bei CSS möglichst bestehende Regeln gezielt ändern und nur neue Komponenten als konsistenten Abschnitt hinzufügen; keine endlose widersprüchliche Override-Schicht. [hidden] darf durch display-Regeln nicht außer Kraft gesetzt werden. Reduzierte Bewegung beachten. Mobile Navigation darf nicht ganzen Bildschirm besetzen, keinen horizontalen Seitenoverflow erzeugen; .leg-picker min-width:0, select width:100%. Auf 390px notfalls Beschriftung Zurück/Weiter knapp, aber weiter verständlich.

## Übergabe
Lies tatsächliche CSS, implementiere die Änderungen. Nenne konkret Änderungen, statische Prüfungen, Grenzen. Keine ausgeführten Browser-/Shelltests behaupten. Astra baut/testet und prüft deine tatsächlichen CSS-Änderungen. Nach Abschluss folgt separate Read-only-Review des eingefrorenen Gesamtstands durch dich.
