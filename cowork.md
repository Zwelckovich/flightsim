# Cowork: Astra / Codex und Claude Opus gemeinsam am Projekt

Diese Anleitung beschreibt den am WorldTour-V2-Projekt erprobten Ablauf und dient als Arbeitsanweisung für weitere Projekte. Stand: 24.09.2026. Der Nutzer gibt den Auftrag; Astra oder Claude übernimmt ausdrücklich die Koordination von Implementierung, Austausch, Tests und gegenseitigen Reviews. Der erste erprobte Weg ist Astra → Claude Code CLI; Abschnitt 10 ergänzt den vorbereiteten Rückweg Claude Code → Codex CLI und den tatsächlichen, vor Modellstart gescheiterten Startversuch.

**Feste Präferenzen: Claude Opus 5.5 mit Max Effort und Codex GPT-6 Astra mit Max Effort.** Claude: Modell-ID `claude-opus-5-5`, Parameter `--effort max`. Codex: Modell-ID `gpt-6-astra`, Konfiguration `model_reasoning_effort="max"`. Kein stiller Wechsel auf ein anderes Modell oder eine geringere Denkstufe. Beide Modelle prüfen die Arbeit des jeweils anderen unabhängig.

## 1. Zuständigkeiten und Austausch

Im ursprünglichen Modus ist Astra der Koordinator: Repository und vorhandene Änderungen lesen, Arbeit aufteilen, Auftragsdateien schreiben, Claude starten, Ergebnisse auswerten, Tests ausführen und den Abschluss zusammenführen. Opus erhält begrenzte Implementierungs- oder Review-Aufträge mit den benötigten Projektinformationen.

Die Kommunikation läuft über **Dateien im gemeinsamen Projekt und CLI-Ergebnisprotokolle**. Der bisherige Opus-Runner erzeugt pro Auftrag eine neue Sitzung; diese kennt die bisherige Unterhaltung nicht automatisch. Für Codex ist eine Fortsetzung über eine explizite Sitzungs-ID vorgesehen; deren erfolgreicher Modellaufruf ist hier noch nicht nachgewiesen (Abschnitt 10). Der Nutzer muss keine Antworten zwischen Chats kopieren. Eine bereits vorhandene Claude-Webunterhaltung wird damit nicht fortgesetzt.

Parallel arbeiten ist sinnvoll, wenn die Dateibereiche unabhängig sind. Beispiel aus WorldTour: Astra bearbeitet `app.js`, CSS und Sync-Tests; Opus bearbeitet `content.json`, Build, Integrator und Datenprüfungen. Pro Datei gibt es genau einen schreibenden Bearbeiter. Änderungen an der vereinbarten Schnittstelle werden vorher abgestimmt.

Bei untrennbaren Änderungen nacheinander arbeiten oder getrennte Git-Worktrees verwenden. Der vorhandene Runner arbeitet direkt im gemeinsamen Projekt; Worktrees richtet er nicht selbst ein.

## 2. Ablauf für einen neuen Auftrag

1. **Ausgangsstand prüfen und sichern.** Projektanweisungen lesen, Git-Status prüfen, vorhandene Nutzeränderungen erhalten. Bei uncommittierten Dateien einen Snapshot mit Hashes erstellen. Nichts zurücksetzen, nur um einen sauberen Ausgangspunkt zu erhalten.
2. **Ergebnis und Dateizuständigkeit festlegen.** Beschreiben, was fertig sein soll, welche Dateien jeder ändern darf und welche Daten unverändert bleiben. Gemeinsame Datenfelder, Statuswerte und Schnittstellen vorab vereinbaren.
3. **Aufträge als Markdown speichern.** Absolute Projektpfade, relevante Quellen, erlaubte Dateien, Prüfungen und erwartete Übergabe nennen. Eine begrenzte Implementierung und eine unabhängige Review sind getrennte Aufträge.
4. **Die Gegenseite starten und lokal weiterarbeiten.** Implementierung parallel nur auf getrennten Dateien. Eindeutiger Laufname pro Aufruf. Der Opus-Runner vergibt eine neue Session-ID; Codex liefert seine Thread-ID beim Start selbst; der Koordinator verwendet sie für Folgeaufträge wieder. Protokolle auf Fehler, verweigerte Werkzeuge und das tatsächlich verwendete Modell prüfen.
5. **Übergabe abwarten.** Ein Übergabebericht benennt Änderungen, tatsächlich ausgeführte Prüfungen, offene Fragen und Einschränkungen. `exit 0` bedeutet nur, dass der CLI-Lauf erfolgreich beendet wurde; der Inhalt kann trotzdem einen Fehler oder eine abgelehnte Review melden.
6. **Passende Tests ausführen.** Im ursprünglichen Opus-Worker-Modus hat Opus keinen Shell-Zugriff; Astra führt Build und Tests aus. Im neuen Koordinatormodus erhält Claude gezielt das Ausführungswerkzeug für den Codex-Aufruf (Abschnitt 10). Ergebnisse prüfen, bevor die nächste abhängige Aktion startet. Eine Fehlermeldung darf nicht durch nachfolgende erfolgreiche Befehle verdeckt werden.
7. **Stand für die Review einfrieren.** Erst nach erfolgreichem Testlauf: aktuelle Diff und SHA-256 der relevanten Dateien sichern. Während der Review diese Dateien nicht ändern.
8. **Gegenseitig reviewen.** Opus prüft Astras Änderungen, Astra prüft Opus' Änderungen. Tatsächlichen Code und Daten lesen, nicht nur die Zusammenfassung. Recherchebehauptungen anhand ausgewählter Primärquellen gegenprüfen. Befunde mit Datei/Stelle, Auswirkung und möglichst einem reproduzierbaren Fall beschreiben.
9. **Korrigieren und gezielt nachprüfen.** Berechtigte Befunde umsetzen, passende Tests erneut ausführen, neuen Stand einfrieren. Die Gegenseite prüft die Korrekturen. Sachlichen Widerspruch begründen; Befunde nicht einfach ungeprüft übernehmen.
10. **Zusammenführen und abnehmen.** Finale Artefakte neu bauen, sicherstellen, dass sie den geprüften Code und Daten enthalten. Hashes mit den freigegebenen Ständen vergleichen. Ausstehende Browser-, Live-System- oder Sim-Prüfungen ausdrücklich nennen. Commit, Push und Veröffentlichung richten sich nach dem konkreten Nutzerauftrag.

**Wichtigste Erfahrung:** Keine Review eines noch bearbeiteten Zwischenstands. Im ersten Arbeitslauf las Opus eine Stelle, während Astra sie gerade korrigierte. Der Befund war für diesen Zwischenstand richtig, aber beim Eintreffen bereits veraltet. Erst die erneute Review des eingefrorenen Endstands gab die Änderung frei.

## 3. Anmeldung und ausführbare Datei

Auf dem verwendeten Windows-Rechner liegt Claude hier:

```text
C:\Users\zwelc\.local\bin\claude.exe
```

Prüfung in PowerShell:

```powershell
$coworkClaude = Join-Path $env:USERPROFILE '.local\bin\claude.exe'
& $coworkClaude --version
& $coworkClaude auth status
```

Falls eine echte Anfrage eine abgelaufene Anmeldung meldet:

```powershell
& $coworkClaude auth login --claudeai
```

Der Nutzer schließt die interaktive Anmeldung einmal ab. Im Testlauf reichte `auth status` allein nicht aus: Der erste Modellaufruf meldete ein abgelaufenes OAuth-Token. Nach der erneuten Anmeldung funktionierte der tatsächliche Aufruf. Keine Zugangsdaten in Auftragsdateien oder Git ablegen.

Der dokumentierte WorldTour-Lauf nutzte Claude Code **2.1.235**. Beim Erstellen dieser Anleitung meldete die lokale CLI **2.1.281**; die unten verwendeten Flags sind auch in deren `--help` vorhanden. Der spätere Koordinatorlauf aus Abschnitt 10 belegt Opus 5.5 unter 2.1.281 mit dem dortigen Werkzeugsatz. Die ursprünglichen Worker-Modi einschließlich WebFetch/WebSearch wurden dabei nicht vollständig erneut getestet. Bei späteren Änderungen erst `--version` und `--help` prüfen.

## 4. Tatsächlich eingesetzter Runner

Vorhandene Datei:

```text
M:\flightsim\VolantaWorldTour\v2\collaboration\run_opus.py
```

So wurden Implementierung und Review aufgerufen:

```powershell
Set-Location -LiteralPath 'M:\flightsim\VolantaWorldTour'

python v2/collaboration/run_opus.py v2/collaboration/2026-09-24/opus-implementation.md opus-implementation

python v2/collaboration/run_opus.py v2/collaboration/2026-09-24/opus-review-astra.md opus-review-astra --review
```

Das sind historische Aufrufe. Für einen neuen Auftrag neue Promptdateien und eindeutige Laufnamen verwenden; bestehende Implementierungsaufträge nicht versehentlich erneut ausführen.

Der Runner erzeugt eine neue UUID, liest den Auftrag als UTF-8, übergibt ihn über `stdin`, schließt den Eingabekanal und wertet anschließend die JSON-Ereignisse aus. Er startet Claude über `subprocess.Popen` mit einer Argumentliste, `shell=False` (Standard) und unter Windows mit `CREATE_NO_WINDOW`. Damit werden Auftragstext und Sonderzeichen nicht als Shell-Befehle interpretiert. Ein sichtbares Terminal ist für diese Aufträge nicht erforderlich.

## 5. Exakter Claude-CLI-Aufruf

Der Runner verwendet für Implementierungen diese Argumente, in dieser Reihenfolge:

```text
C:\Users\zwelc\.local\bin\claude.exe -p --model claude-opus-5-5 --effort max --safe-mode --permission-mode dontAsk --tools Read,Edit,Write,Glob,Grep,WebFetch,WebSearch --allowedTools Read,Edit,Write,Glob,Grep,WebFetch,WebSearch --session-id <NEUE-UUID> --output-format stream-json --verbose
```

`<NEUE-UUID>` wird für jeden Lauf erzeugt. Der vollständige Auftrag kommt über die Standardeingabe, nicht durch Ersetzen des Platzhalters mit Prompttext.

Für Reviews ersetzt der Runner **beide** Werkzeuglisten durch:

```text
Read,Glob,Grep,WebFetch,WebSearch
```

Ein direkt ausführbares PowerShell-Äquivalent für eine Implementierung:

```powershell
Set-Location -LiteralPath 'M:\flightsim\VolantaWorldTour'
$coworkClaude = Join-Path $env:USERPROFILE '.local\bin\claude.exe'
$coworkPromptPath = '.\v2\collaboration\mein-neuer-auftrag.md'  # vorher erstellen
$coworkSession = [guid]::NewGuid().ToString()
$coworkPrompt = Get-Content -LiteralPath $coworkPromptPath -Raw -Encoding UTF8
$coworkPreviousEncoding = $OutputEncoding

try {
    # Relevant für UTF-8-Aufträge in Windows PowerShell.
    $OutputEncoding = [System.Text.UTF8Encoding]::new($false)
    $coworkPrompt | & $coworkClaude -p `
        --model claude-opus-5-5 `
        --effort max `
        --safe-mode `
        --permission-mode dontAsk `
        --tools 'Read,Edit,Write,Glob,Grep,WebFetch,WebSearch' `
        --allowedTools 'Read,Edit,Write,Glob,Grep,WebFetch,WebSearch' `
        --session-id $coworkSession `
        --output-format stream-json `
        --verbose

    if ($LASTEXITCODE -ne 0) {
        throw "Claude-Lauf fehlgeschlagen: Exit-Code $LASTEXITCODE"
    }
} finally {
    $OutputEncoding = $coworkPreviousEncoding
}
```

Für die reguläre Zusammenarbeit den Python-Runner verwenden: Das direkte Beispiel zeigt dieselben CLI-Parameter, übernimmt aber weder automatische Protokolldateien noch die Modell- und Ergebnisprüfung des Runners.

| Parameter | Zweck im Workflow |
|---|---|
| `-p` | Nichtinteraktiver Auftrag mit anschließender Ausgabe und Beendigung. |
| `--model claude-opus-5-5` | Konkretes Modell; kein beweglicher Alias wie `opus`. |
| `--effort max` | Explizit höchste hier gewünschte Denkstufe. Eine Antwortlängen-Vorgabe im Prompt senkt diese Stufe nicht. |
| `--safe-mode` | Deaktiviert benutzerdefinierte Anpassungen wie automatisch geladene CLAUDE.md-Dateien, Skills, Hooks, MCP-Server und Custom Agents. Authentifizierung und normale Berechtigungen bleiben wirksam. |
| `--permission-mode dontAsk` | Keine interaktiven Genehmigungsfragen im Hintergrundlauf; nicht erlaubte Aktionen werden abgewiesen. Das umgeht keine Dateisystem- oder Netzwerksperren. |
| `--tools` | Stellt ausschließlich die genannten eingebauten Werkzeuge bereit. |
| `--allowedTools` | Erlaubt diese Werkzeuge für den unbeaufsichtigten Teil des Auftrags im Rahmen der wirksamen Berechtigungen. |
| `--session-id` | Eindeutige Zuordnung von Auftrag und Sitzung. |
| `--output-format stream-json --verbose` | Maschinenlesbare Zwischenereignisse, Abschluss und Modell-/Nutzungsinformationen. |

Es wird kein `--fallback-model` gesetzt und keine Berechtigungssperre mit `--dangerously-skip-permissions` umgangen. Im Implementierungsmodus sind `Edit` und `Write` verfügbar, im Review-Modus nicht. `Bash`, andere Ausführungswerkzeuge und das Werkzeug zum Starten von Unteragenten sind in keinem dieser beiden Opus-Worker-Modi enthalten. Für Claude als Koordinator ist ein gesondert begrenzter Bash-Aufruf vorgesehen (Abschnitt 10).

**Folge von `--safe-mode`:** Astra muss die relevanten Projektanweisungen selbst lesen und ausdrücklich in den Auftrag übernehmen. Nicht davon ausgehen, dass Opus ein lokales `CLAUDE.md`, einen früheren Chat oder eine Skill-Anweisung kennt. Die Liste erlaubter Dateien im Prompt ist eine Arbeitsvereinbarung, keine technisch erzwungene Dateisystem-Isolation.

## 6. Nachweise und Fehlerbehandlung

Der Runner speichert pro Lauf neben sich in `.runs/`:

- `<laufname>.meta.json`: Modell, Effort, Session-ID, Promptpfad und Review-Modus.
- `<laufname>.events.jsonl`: vollständige Ereignisse während des Auftrags.
- `<laufname>.stderr.log`: CLI-Fehlerausgabe.
- `<laufname>.result.json`: maschinenlesbarer Abschluss.
- `<laufname>.result.md`: lesbarer Ergebnistext.

Die Rohprotokolle sind im erprobten Projekt per `.gitignore` ausgeschlossen. Sie können vollständige Projektinhalte und lange Ausgaben enthalten. Ins nachvollziehbare Projektprotokoll kommen Aufträge, ausgewählte Übergaben, Reviews, Testresultate und relevante Hashes.

Der Runner kontrolliert das Modell beim `system/init`-Ereignis und beendet den Lauf, wenn es nicht `claude-opus-5-5` ist. Astra kontrolliert außerdem `modelUsage` / `canonicalModel`, `is_error`, `permission_denials` und den eigentlichen Ergebnistext. Ohne verwertbaren Abschlussbericht keine erfolgreiche Übergabe behaupten. Bei einem nicht verfügbaren Modell oder Werkzeug den konkreten Fehler behandeln, statt still eine andere Konfiguration zu verwenden.

Transparenz aus dem Testlauf: Implementierung und Reviews liefen auf Opus 5.5. Das eingebaute CLI-Werkzeug `WebFetch` nutzte laut Nutzungsmetadaten zusätzlich **Haiku 4.5 für Webseitenzusammenfassungen**. Daher zentrale Behauptungen unabhängig an Primärquellen prüfen und den Modellnachweis nicht als Behauptung verstehen, intern sei ausnahmslos jeder Hilfsaufruf Opus gewesen.

Der Runner versendet nach dem Start keine weiteren Nachrichten in den laufenden Auftrag; sein `stdin` ist geschlossen. Eine Rückmeldung oder Korrektur wird als neuer begrenzter Auftrag mit Verweisen auf die bisherigen Berichte gestartet. Bei einem Abbruch zuerst Teiländerungen und Protokolle prüfen, bevor derselbe Auftrag erneut läuft. Neue Laufnamen verhindern das Überschreiben früherer Protokolle.

## 7. Auftragsvorlage

```markdown
# Aufgabe: <konkretes Ergebnis>

Projekt: <absoluter Projektpfad>
Modell: <Opus 5.5 mit Max Effort oder GPT-6 Astra mit Max Effort>.

## Kontext und Regeln
<Nutzerziel, relevante Projektanweisungen und begründete Entscheidungen.>

## Änderungsspielraum
Du darfst ausschließlich diese Dateien ändern: <Liste>.
<Andere Person> bearbeitet parallel: <Liste>.
Erhalten bleiben müssen: <Daten, Schnittstellen, IDs, Nutzeränderungen>.
Keine Unteragenten. Commit/Push/Veröffentlichung: <konkreter Auftragsumfang>.

## Aufgabe und Abnahmekriterien
<Begrenzte Arbeit, erwartetes Verhalten, Randfälle, ggf. Primärquellen.>

## Prüfungen und Übergabe
<Sinnvolle Testbefehle bzw. Prüfschritte.>
Du hast in diesem Modus keine Shell. Behaupte keine ausgeführten Tests;
Astra führt sie nach der Übergabe aus.
Schreibe einen knappen Bericht: geänderte Dateien, Begründung,
statisch geprüfte Punkte und verbleibende Grenzen.
Ergebnisdatei: <absoluter Pfad>.
```

Für die Review den Änderungsspielraum durch „nur lesen“ ersetzen. Geprüfte Dateien, Baseline/Diff, Testprotokoll und Hashmanifest nennen. Konkrete Befunde verlangen und ausdrücklich erlauben, einer vorgeschlagenen Änderung zu widersprechen. Nach einer Korrektur nur den betroffenen Befund erneut prüfen lassen, solange kein neuer Anlass für einen Gesamtaudit besteht.

## 8. Auf ein anderes Projekt übertragen

Den Runner kann man beispielsweise nach `<Projekt>/.collaboration/run_opus.py` kopieren. Dann müssen seine Pfade bewusst angepasst werden: Im vorhandenen WorldTour-Runner ist `project = Path(__file__).resolve().parents[2]`, weil er unter `v2/collaboration/` liegt. Bei `.collaboration/run_opus.py` wäre der Projektordner `parents[1]`. Einfaches Kopieren ohne Anpassung kann Claude im falschen Arbeitsverzeichnis starten.

Die aktuelle Implementierung erwartet Windows, Python 3 und die oben genannte lokale Claude-Installation. Für ein anderes Betriebssystem sind insbesondere ausführbarer CLI-Pfad und `CREATE_NO_WINDOW` anzupassen. Auftragsdatei möglichst absolut angeben oder den Runner aus dem Projektordner starten; sie wird relativ zum aufrufenden Prozess gelesen.

Sinnvolle Ablage pro künftigem Arbeitslauf:

```text
<Projekt>/
  cowork.md
  .collaboration/
    run_opus.py
    .runs/                  # Rohprotokolle, ignoriert
    <datum>-<thema>/
      brief.md
      opus-implementation.md
      opus-implementation-result.md
      opus-review-astra.md
      opus-review-astra-result.md
      astra-review-opus.md
      corrections.md
      review-manifest.json
      validation.json
      README.md
```

Der ausdrücklich gewählte Koordinator führt den Austausch weiter, solange der aktive Auftrag läuft. Der Runner allein richtet keinen dauerhaften Hintergrunddienst und keine wiederkehrende Automation ein. Für spätere Projekte reicht als Nutzerauftrag beispielsweise:

> Arbeitet nach cowork.md gemeinsam an diesem Projekt. Claude Opus 5.5 mit Max Effort, getrennte Zuständigkeiten und gegenseitige Reviews. Koordiniere den Austausch selbstständig und dokumentiere den geprüften Endstand.

## 9. Referenz des ersten Durchlaufs

- Projekt: `M:\flightsim\VolantaWorldTour`
- Ablauf und Ergebnis: `VolantaWorldTour/v2/collaboration/2026-09-24/README.md`
- Tatsächliche Aufträge und Reviews: derselbe Ordner.
- Modellnachweise: `model-runs.json` in diesem Ordner.
- Prüfresultate und finale Hashes: `validation.json` in diesem Ordner.
- Implementierte Aufteilung: Astra – Sync, UI und Regressionen; Opus – Szeneriedaten, Build und Importer.
- Ergebnis: beide Seiten fanden konkrete Fehler in der Arbeit der anderen; Korrekturen wurden erneut geprüft. Einschränkungen bei Live-Cloud, Browser und Simulator blieben ausdrücklich dokumentiert.

## 10. Rückweg: Claude koordiniert, Codex arbeitet

**Teststand 24.09.2026:** Claude hat Codex tatsächlich gestartet. Der Start scheiterte vor dem Modellaufruf mit „Zugriff verweigert“ bei der App-Server-Initialisierung. Die begleitenden Warnungen und eine separate Schreibprobe belegen fehlenden Schreibzugriff auf das lokale Codex-Datenverzeichnis; als Ursache des fatalen Fehlers liegt dies nahe, ist aber nicht abschließend nachgewiesen. Es gab keine Thread-ID, keine Dateiänderung und keinen Fortsetzungsturn. Dieser Abschnitt dokumentiert den Startversuch und den vorbereiteten Rückweg; einen erfolgreichen Ende-zu-Ende-Test behauptet er nicht.

**Rollen.** Die Rollen sind symmetrisch. Wer koordiniert, schreibt Aufträge, startet die andere Seite per CLI, prüft Protokolle und tatsächliche Dateien, veranlasst Tests und führt zusammen; die andere Seite bearbeitet begrenzte Aufträge. Die Regeln aus Abschnitten 1, 2 und 7 gelten mit den jeweiligen Modell- und Werkzeugangaben in beide Richtungen. Es gibt genau einen Koordinator pro Auftrag. Worker starten nicht rekursiv weitere Koordinatoren. Nach erfüllten Abnahmekriterien und behobenen relevanten Review-Befunden endet der Arbeitslauf. Im Rückweg koordiniert Claude Opus 5.5 über die Claude Code CLI und startet eine **eigene** Codex-CLI-Sitzung mit GPT-6 Astra. Die laufende Codex-Desktop-Unterhaltung übernimmt Claude nicht: nicht fortsetzen, nicht steuern, nicht hineinschreiben. Ergebnisse gehen über Dateien und Protokolle zurück. In Codex-Aufträgen den gesamten Absatz der Vorlage ab „Du hast in diesem Modus keine Shell“ bis „Astra führt sie nach der Übergabe aus“ ersetzen: „Führe die vereinbarten Prüfungen aus, soweit deine Sandbox sie erlaubt. Nenne die tatsächlich ausgeführten Befehle, Ergebnisse und blockierten Prüfungen.“ Die unabhängige Gegenprüfung braucht einen benannten Ausführer mit separat erlaubten Testbefehlen oder einen getrennten Prüfauftrag; der nur zum CLI-Start erlaubte Bash-Aufruf reicht dafür nicht. Vor Arbeitsbeginn festlegen, wer diese Tests ausführt. Im vorliegenden Versuch war Astra dafür vorgesehen; mangels Codeänderung fand kein Laufzeittest statt. Ohne ausführbare unabhängige Prüfungen keine Testabnahme behaupten.

**Feste Einstellungen.** Codex: `-m gpt-6-astra` und `-c model_reasoning_effort="max"`. Koordinator: `--model claude-opus-5-5 --effort max`. Kein Fallback, keine niedrigere Stufe. Fehlt ein Modell, eine Stufe oder ein Recht, ist der Lauf fehlgeschlagen und wird so gemeldet.

**Codex-Aufruf.** Argumente als Liste ohne Shell übergeben, z. B. mit Python `subprocess.Popen(args, cwd=<Projekt>, shell=False)`, unter Windows mit `CREATE_NO_WINDOW`. Den Auftrag als UTF-8 über stdin senden und stdin schließen; stdout nach `<lauf>.events.jsonl`, stderr nach `<lauf>.stderr.log`. `model_reasoning_effort="max"` ist *ein* Argument einschließlich der Anführungszeichen. Ein PowerShell-Aufruf wurde nicht getestet.

Start, im Test genau so übergeben:

```text
<codex.exe> -a never exec --ignore-user-config -C <Projekt> --sandbox workspace-write -m gpt-6-astra -c model_reasoning_effort="max" -c agents.enabled=false --skip-git-repo-check --json -o <lauf>.last.md -
```

Folgeauftrag in derselben Sitzung, vorbereitet, nicht ausgeführt. Astra hat die Syntax lokal mit `codex exec resume --help` geprüft. Die Resume-Hilfe führt `-m`, `-c`, `--json`, `-o`, `--ignore-user-config` und `--skip-git-repo-check` auf, aber nicht `--sandbox` und `-C`. Diese stehen deshalb vor `resume`. Ob sie dort für den Fortsetzungsturn wirken, ist ungetestet:

```text
<codex.exe> -a never exec --ignore-user-config -C <Projekt> --sandbox workspace-write -m gpt-6-astra -c model_reasoning_effort="max" -c agents.enabled=false --skip-git-repo-check resume --json -o <lauf>.last.md <THREAD-UUID> -
```

Im Test war `<codex.exe>` = `C:\Users\zwelc\AppData\Local\OpenAI\Codex\bin\80f78947ad880e6e\codex.exe`. Vor neuen Läufen Pfad, `--version` sowie die Hilfe zu `exec` und `exec resume` prüfen. `--skip-git-repo-check` nur für Ordner ohne Git-Repository.

| Argument | Zweck |
|---|---|
| `-a never` | Keine Genehmigungsfragen; Verbotenes scheitert, statt eskaliert zu werden. |
| `exec` / `exec … resume <UUID>` | Nichtinteraktiver Lauf bzw. Fortsetzung genau dieser Sitzung. |
| `--ignore-user-config` | `$CODEX_HOME/config.toml` nicht laden; die Anmeldung nutzt laut Hilfe weiterhin `CODEX_HOME`. |
| `-C <Projekt>` | Explizites Arbeitsverzeichnis. |
| `--sandbox workspace-write` | Schreibt im Arbeitsverzeichnis und, je nach Umgebung, in weiteren erlaubten Wurzeln und temporären Verzeichnissen; keine Umgehung. Keine Beschränkung auf einzelne Dateien, die Dateiliste im Auftrag bleibt Arbeitsvereinbarung. |
| `-c agents.enabled=false` | Laut [Konfigurationsreferenz](https://learn.chatgpt.com/docs/config-file/config-reference) Unteragenten deaktivieren. Im Versuch nur übergeben; die Wirkung wurde mangels Modellturn nicht geprüft. |
| `--json` / `-o <Datei>` | JSONL-Ereignisse auf stdout / letzte Antwort als Datei. |
| `-` | Auftrag von stdin. |

**Prüfung nach jedem Lauf.**

- Exit-Code 0; `thread.started` mit `thread_id`, beim Folgeauftrag dieselbe ID (erwartet, ungetestet).
- `turn.completed` vorhanden, kein `turn.failed` oder `error`.
- `-o`-Datei vorhanden; ihr Inhalt ist ein verwertbarer Übergabebericht.
- stderr immer lesen: Im Test blieb stdout leer, der Fehler stand nur in stderr. Eine Suche nach Fehlerereignissen allein fand nichts.
- Geänderte Dateien selbst lesen; `exit 0` allein ist keine erfolgreiche Übergabe.
- Modellnachweis: Welche Modellangaben die Codex-Ereignisse enthalten, ist ungeprüft. Bis dahin ist nur die Übergabe der Argumente belegt, nicht die tatsächliche Nutzung.

**Sitzung steuern.** Codex vergibt die Thread-ID selbst. Der Koordinator übernimmt sie aus `thread.started` seines eigenen Startlaufs und nennt sie bei Folgeaufträgen exakt. Kein `--last`, denn es trifft nicht sicher die eigene Sitzung. Folgeaufträge erst nach abgeschlossenem Turn senden. Einreihen oder Live-Steuern in einen laufenden Turn ist nicht getestet und nicht Teil des Ablaufs. `--ephemeral` (Codex) und `--no-session-persistence` (Claude) hinterlassen keine fortsetzbare Sitzung: nur für Einmalläufe, nie für Sitzungen, die per `resume` weiterlaufen sollen. Der Claude-Koordinator lief im Test mit `--no-session-persistence`.

**Berechtigungen im Koordinatormodus.** Der Opus-Worker-Modus (Abschnitt 5) bleibt ohne Bash. Als Koordinator braucht Claude ein Ausführungswerkzeug, begrenzt auf den Codex-Runner. Im Test gestartet mit:

```text
claude.exe -p --model claude-opus-5-5 --effort max --safe-mode --permission-mode dontAsk --tools Read,Edit,Write,Glob,Grep,Bash --allowedTools Read,Edit,Write,Glob,Grep "Bash(C:/Python314/python.exe *)" --session-id <NEUE-UUID> --no-session-persistence --output-format stream-json --verbose
```

Die beiden Werte nach `--allowedTools` sind getrennte Argumente. Der Runner-Aufruf wurde damit unter `dontAsk` ausgeführt. Die Regel erlaubt technisch aber jedes Python-Skript; die Beschränkung auf den Runner war nur eine Auftragsregel. Wo möglich, die Regel enger fassen (ungetestet).

Die hier verwendete Standardablage liegt unter `%USERPROFILE%\.codex`. Die CLI meldete dort fehlende Schreibrechte beim Anlegen eines arg0-Verzeichnisses; separat scheiterte ihre App-Server-Initialisierung mit `failed to initialize in-process app-server client: Zugriff verweigert (os error 5)`. Die fatale Meldung nennt selbst keinen Pfad. Der Zusammenhang mit dem fehlenden Schreibrecht ist eine naheliegende, noch nicht abschließend bestätigte Ursache. Ein beschreibbarer Projektordner allein machte den Aufruf in dieser Umgebung nicht lauffähig. Die für diesen Versuch angeforderte Freigabe wurde erteilt; der gestartete Prozess konnte dennoch nicht schreiben. Nach der Neuinitialisierung des Node-Prozesses wurde nur eine gezielte Schreibprobe wiederholt, die erneut mit EPERM scheiterte; ein zweiter Codex-Start wurde nicht versucht. Bei einer Wiederholung zuerst prüfen, ob die bereits genehmigten Rechte im tatsächlich ausführenden Prozess wirksam sind. Fehlende zusätzliche Rechte gezielt über den vorgesehenen Freigabeweg einholen; keine Sandbox pauschal abschalten und keine Authentifizierungsdateien kopieren. Auch kein Ersatz-`CODEX_HOME` mit kopierten Anmeldedateien verwenden. Ob Codex aus dieser Umgebung das Netzwerk erreicht, ist ungeprüft.

**Reviews.** Weiterhin gegenseitig und nur auf eingefrorenem Stand (Diff und SHA-256, Abschnitt 2 Schritt 7): Claude prüft Codex-Änderungen, Astra prüft Claudes Änderungen. Für Codex-Reviews ist `--sandbox read-only` das naheliegende Gegenstück zum Opus-Review-Modus (ungetestet). Vom Worker genannte Prüfungen ersetzen keine unabhängigen Tests.

**Aufräumen nach Tests.** Nur selbst erzeugte Testartefakte entfernen: Promptdateien, `<lauf>.invocation.json`, `.events.jsonl`, `.stderr.log`, `.result.json`, `.pid`, `.last.md` und temporäre Runner. Eine erzeugte Codex-Testsitzung nur über ihre exakte Thread-ID entfernen: `codex delete --force <TEST-THREAD-UUID>` (lokale Hilfe bestätigt den Befehl; hier mangels Sitzung nicht ausgeführt). Vorher sicherstellen, dass diese UUID aus dem eigenen abgeschlossenen Test stammt. Keine Muster, keine anderen Sitzungen, nie die Desktop-Unterhaltung. Im Test entstand keine Thread-ID; es ist also keine Codex-Testsitzung identifiziert, und auf Verdacht wird nichts gelöscht.

**Versionen.** Claude Code 2.1.281, belegt durch `system/init` des Koordinators. Codex CLI 0.155.0-alpha.16.3 laut Astras lokaler Prüfung; der abgebrochene Lauf gab keine Version aus.

### Nachweis für den nächsten erfolgreichen Test

Der Koordinator lässt Codex zunächst eine kleine, ausschließlich für den Test erzeugte Datei korrigieren. Nach eigenständiger Kontrolle sendet er eine begrenzte Erweiterung über die erhaltene Thread-ID. Erfolg verlangt zwei abgeschlossene Turns in derselben Sitzung, überprüfte Dateiänderungen und unabhängig ausgeführte Laufzeittests. Eine nur im ersten Turn genannte Kennung kann zusätzlich den Gesprächskontext prüfen; im Folgeprotokoll muss erkennbar sein, dass Codex sie nicht aus einer Prompt- oder Protokolldatei gelesen hat.

Vor dem Schlussreview Dateien und Hashes einfrieren. Claude prüft Astras Integration, Astra prüft Claudes Beitrag. Fehlerberichte bleiben Fehlerberichte, auch wenn der äußere Claude-Prozess mit Exit 0 abschließt. Der Ausführer, der Claude startet (hier Astra), prüft den äußeren Claude-Prozess. Claude prüft als Koordinator den inneren Codex-Prozess und dessen inhaltliche Ergebnisse; der externe Ausführer kontrolliert die Übergabe zusätzlich anhand der gespeicherten Nachweise.

### Quellen und Nachweisgrenzen

Die genauen Parameter wurden mit den lokal installierten CLI-Hilfen geprüft. Der gebündelte Codex-Modellkatalog nennt `gpt-6-astra` mit `max`; dies belegt die angebotene Konfiguration, noch keine erfolgreiche Anfrage.

- [Codex: nichtinteraktive Aufträge und Fortsetzung](https://learn.chatgpt.com/docs/non-interactive-mode)
- [Codex: Konfigurationsreferenz](https://learn.chatgpt.com/docs/config-file/config-reference)
- [GPT-6 Astra: Modell und Reasoning-Stufen](https://developers.openai.com/api/docs/models/gpt-6-astra)

Die temporären Versuchsdateien dienen nur der Durchführung und werden nach Übernahme der geprüften Erkenntnisse entfernt. Bestehende Projekt-Regressionstests und die Dokumentation des ersten WorldTour-Arbeitslaufs gehören nicht zu dieser Bereinigung.
