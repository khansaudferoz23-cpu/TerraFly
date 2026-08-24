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
Write-Host "Press Ctrl+C here to stop it."
try {
    while (-not $backend.HasExited -and -not $frontend.HasExited) { Start-Sleep -Seconds 1 }
} finally {
    if (-not $backend.HasExited) { Stop-Process -Id $backend.Id }
    if (-not $frontend.HasExited) { Stop-Process -Id $frontend.Id }
}
