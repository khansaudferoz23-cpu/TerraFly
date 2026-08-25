$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$python = "$projectRoot\.venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $python)) {
    throw "TerraFly is not set up. Run scripts\setup.ps1 once first."
}

$env:HF_HOME = "$projectRoot\runtime\model-cache"
$backend = Start-Process -FilePath $python -ArgumentList @("-m", "uvicorn", "terrafly.main:app", "--host", "127.0.0.1", "--port", "8000") -WorkingDirectory $projectRoot -WindowStyle Hidden -PassThru
$frontend = Start-Process -FilePath "npm.cmd" -ArgumentList @("run", "dev") -WorkingDirectory "$projectRoot\frontend" -WindowStyle Hidden -PassThru
Write-Host "TerraFly is starting at http://127.0.0.1:5173" -ForegroundColor Green
$ready = $false
for ($attempt = 0; $attempt -lt 40; $attempt++) {
    if ($backend.HasExited -or $frontend.HasExited) { break }
    try {
        $response = Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:5173" -TimeoutSec 1
        if ($response.StatusCode -eq 200) { $ready = $true; break }
    } catch {
        Start-Sleep -Milliseconds 500
    }
}
if ($ready) {
    Start-Process "http://127.0.0.1:5173"
    Write-Host "TerraFly is ready. Your browser should open automatically." -ForegroundColor Green
} else {
    Write-Warning "TerraFly did not become ready. Keep this window open and review any setup errors."
}
Write-Host "Keep this window open. Press Ctrl+C here to stop TerraFly."
try {
    while (-not $backend.HasExited -and -not $frontend.HasExited) { Start-Sleep -Seconds 1 }
} finally {
    if (-not $backend.HasExited) { Stop-Process -Id $backend.Id }
    if (-not $frontend.HasExited) { Stop-Process -Id $frontend.Id }
}
