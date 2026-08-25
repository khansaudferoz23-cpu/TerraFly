param([switch]$Full)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot ".venv\Scripts\python.exe"
$frontend = Join-Path $projectRoot "frontend"

function Invoke-Check {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][scriptblock]$Action
    )
    Write-Host "`n[CHECK] $Name" -ForegroundColor Cyan
    & $Action
    if ($LASTEXITCODE -ne 0) { throw "$Name failed with exit code $LASTEXITCODE." }
    Write-Host "[PASS]  $Name" -ForegroundColor Green
}

if (-not (Test-Path -LiteralPath $python)) {
    throw "TerraFly is not set up. Run scripts\setup.ps1 once first."
}
if (-not (Test-Path -LiteralPath (Join-Path $frontend "node_modules"))) {
    throw "Frontend packages are missing. Run scripts\setup.ps1 once first."
}

Push-Location $projectRoot
try {
    Invoke-Check "Python dependencies" { & $python -m pip check }
    Invoke-Check "Backend scientific and safety tests" { & $python -m pytest -q }
    Invoke-Check "Frontend interaction tests" { Push-Location $frontend; try { npm test } finally { Pop-Location } }
    Invoke-Check "Production interface build" { Push-Location $frontend; try { npm run build } finally { Pop-Location } }

    if ($Full) {
        $env:HF_HOME = Join-Path $projectRoot "runtime\model-cache"
        $device = (& $python -c "import torch; print('cuda' if torch.cuda.is_available() else 'cpu')").Trim()
        Invoke-Check "Complete real-model calibration workflow on $device" {
            & $python scripts\smoke_final_workflow.py --device $device
        }
    }

    try {
        $health = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/health" -TimeoutSec 2
        if ($health.service -ne "TerraFly" -or $health.version -ne "1.0.0") {
            throw "Running service identity/version does not match TerraFly 1.0.0."
        }
        Write-Host "`n[PASS]  Running app health: TerraFly $($health.version)" -ForegroundColor Green
    } catch [System.Net.WebException] {
        Write-Host "`n[INFO]  App is not running; launch it with Start-TerraFly.cmd for the visual check." -ForegroundColor Yellow
    }

    Write-Host "`nALL REQUESTED TERRAFLY CHECKS PASSED." -ForegroundColor Green
    Write-Host "Automated checks prove software behavior; they do not replace independent height validation."
} finally {
    Pop-Location
}
