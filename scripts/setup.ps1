$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$bundledPython = Join-Path $env:USERPROFILE ".cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"

if (-not (Test-Path -LiteralPath "$projectRoot\.venv\Scripts\python.exe")) {
    if (Test-Path -LiteralPath $bundledPython) {
        & $bundledPython -m venv "$projectRoot\.venv"
    } else {
        py -3.12 -m venv "$projectRoot\.venv"
    }
}

& "$projectRoot\.venv\Scripts\python.exe" -m pip install --upgrade pip
& "$projectRoot\.venv\Scripts\python.exe" -m pip install -e "$projectRoot[test,ml]"
& "$projectRoot\.venv\Scripts\python.exe" -m pip install -r "$projectRoot\requirements-ml-cu130.txt"
Push-Location "$projectRoot\frontend"
try { npm install } finally { Pop-Location }
Write-Host "TerraFly setup complete." -ForegroundColor Green
\n