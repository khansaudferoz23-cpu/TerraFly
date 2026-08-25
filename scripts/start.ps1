$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot ".venv\Scripts\python.exe"
$logRoot = Join-Path $projectRoot "runtime\logs"

function Test-TerraFlyEndpoint {
    param(
        [Parameter(Mandatory = $true)][string]$Uri,
        [Parameter(Mandatory = $true)][string]$ExpectedMarker
    )
    try {
        $response = Invoke-WebRequest -UseBasicParsing -Uri $Uri -TimeoutSec 1
        return $response.StatusCode -eq 200 -and $response.Content.Contains($ExpectedMarker)
    } catch {
        return $false
    }
}

function Assert-PortAvailable {
    param([Parameter(Mandatory = $true)][int]$Port)
    $listener = Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue
    if ($listener) {
        $owners = ($listener | Select-Object -ExpandProperty OwningProcess -Unique) -join ", "
        throw "Port $Port is already used by another program (process $owners). Close it, then start TerraFly again."
    }
}

if (-not (Test-Path -LiteralPath $python)) {
    throw "TerraFly is not set up. Run scripts\setup.ps1 once first."
}

New-Item -ItemType Directory -Path $logRoot -Force | Out-Null
$env:HF_HOME = Join-Path $projectRoot "runtime\model-cache"
$backend = $null
$frontend = $null
$backendReady = Test-TerraFlyEndpoint "http://127.0.0.1:8000/api/health" '"service":"TerraFly"'
$frontendReady = Test-TerraFlyEndpoint "http://127.0.0.1:5173" "TerraFly"

try {
    if (-not $backendReady) {
        Assert-PortAvailable 8000
        $backend = Start-Process -FilePath $python `
            -ArgumentList @("-m", "uvicorn", "terrafly.main:app", "--host", "127.0.0.1", "--port", "8000") `
            -WorkingDirectory $projectRoot -WindowStyle Hidden -PassThru `
            -RedirectStandardOutput (Join-Path $logRoot "backend-output.log") `
            -RedirectStandardError (Join-Path $logRoot "backend-error.log")
    } else {
        Write-Host "Using the TerraFly backend that is already running." -ForegroundColor DarkGray
    }

    if (-not $frontendReady) {
        Assert-PortAvailable 5173
        $frontend = Start-Process -FilePath "npm.cmd" -ArgumentList @("run", "dev") `
            -WorkingDirectory (Join-Path $projectRoot "frontend") -WindowStyle Hidden -PassThru `
            -RedirectStandardOutput (Join-Path $logRoot "frontend-output.log") `
            -RedirectStandardError (Join-Path $logRoot "frontend-error.log")
    } else {
        Write-Host "Using the TerraFly interface that is already running." -ForegroundColor DarkGray
    }

    Write-Host "TerraFly is starting at http://127.0.0.1:5173" -ForegroundColor Green
    for ($attempt = 0; $attempt -lt 60; $attempt++) {
        if (($backend -and $backend.HasExited) -or ($frontend -and $frontend.HasExited)) { break }
        $backendReady = Test-TerraFlyEndpoint "http://127.0.0.1:8000/api/health" '"service":"TerraFly"'
        $frontendReady = Test-TerraFlyEndpoint "http://127.0.0.1:5173" "TerraFly"
        if ($backendReady -and $frontendReady) { break }
        Start-Sleep -Milliseconds 500
    }

    if (-not ($backendReady -and $frontendReady)) {
        throw "TerraFly did not become ready. Review the readable logs in runtime\logs, then run this launcher again."
    }

    Start-Process "http://127.0.0.1:5173"
    Write-Host "TerraFly is ready. Your browser should open automatically." -ForegroundColor Green
    Write-Host "Keep this window open. Press Ctrl+C here to stop services started by this launcher."
    while (($null -eq $backend -or -not $backend.HasExited) -and ($null -eq $frontend -or -not $frontend.HasExited)) {
        Start-Sleep -Seconds 1
    }
} finally {
    if ($backend -and -not $backend.HasExited) { Stop-Process -Id $backend.Id }
    if ($frontend -and -not $frontend.HasExited) { Stop-Process -Id $frontend.Id }
}
