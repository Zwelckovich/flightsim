param([switch]$RebuildScenery)

$ErrorActionPreference = 'Stop'
# This script belongs beside work/; its copy in outputs/ also resolves the project.
$projectRoot = $PSScriptRoot
if (-not (Test-Path -LiteralPath (Join-Path $projectRoot 'work') -PathType Container)) {
    $projectRoot = Split-Path -Parent $projectRoot
}
if (-not (Test-Path -LiteralPath (Join-Path $projectRoot 'work/build_html.py') -PathType Leaf)) {
    throw 'Projektordner mit work/build_html.py nicht gefunden.'
}
$pythonCommand = Get-Command python -CommandType Application -ErrorAction Stop | Select-Object -First 1
$nodeCommand = Get-Command node -CommandType Application -ErrorAction Stop | Select-Object -First 1
$env:PYTHONIOENCODING = 'utf-8'

function Invoke-PythonStep([string]$relativePath) {
    & $pythonCommand.Source -B (Join-Path $projectRoot $relativePath)
    if ($LASTEXITCODE -ne 0) { throw "Fehler in $relativePath (Exitcode $LASTEXITCODE)." }
}

if ($RebuildScenery) {
    Invoke-PythonStep 'work/build_scenery_guide.py'
    Invoke-PythonStep 'work/build_comparison.py'
}
Invoke-PythonStep 'work/check_debriefs.py'
Invoke-PythonStep 'work/build_html.py'
Invoke-PythonStep 'work/validate.py'
& $nodeCommand.Source --check (Join-Path $projectRoot 'work/app-check.js')
if ($LASTEXITCODE -ne 0) { throw 'JavaScript-Syntaxprüfung fehlgeschlagen.' }
& $nodeCommand.Source (Join-Path $projectRoot 'work/check_excursions.cjs')
if ($LASTEXITCODE -ne 0) { throw 'Projektprüfungen fehlgeschlagen.' }
& $nodeCommand.Source (Join-Path $projectRoot 'work/check_debriefs.cjs')
if ($LASTEXITCODE -ne 0) { throw 'Debriefing-Prüfungen fehlgeschlagen.' }
& $nodeCommand.Source (Join-Path $projectRoot 'work/check_resets.cjs')
if ($LASTEXITCODE -ne 0) { throw 'Reset-Prüfungen fehlgeschlagen.' }
Copy-Item -LiteralPath (Join-Path $projectRoot 'outputs/Volanta-Worldtour-EDLV.html') -Destination (Join-Path $projectRoot 'Volanta-Worldtour-EDLV.html') -Force
Write-Output ('Fertig: ' + (Join-Path $projectRoot 'Volanta-Worldtour-EDLV.html'))
