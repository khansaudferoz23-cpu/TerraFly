param([string]$Destination)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
if (-not $Destination) { $Destination = Join-Path (Split-Path -Parent $projectRoot) "outputs" }
$destinationRoot = [System.IO.Path]::GetFullPath($Destination)
$stage = Join-Path $destinationRoot "TerraFly_FINAL_WINDOWS"
$sourceArchive = Join-Path $destinationRoot "TerraFly_FINAL_SOURCE.zip"
$releaseArchive = Join-Path $destinationRoot "TerraFly_FINAL_WINDOWS.zip"
$checksumFile = Join-Path $destinationRoot "TerraFly_FINAL_SHA256.txt"

foreach ($path in @($stage, $sourceArchive, $releaseArchive, $checksumFile)) {
    if (Test-Path -LiteralPath $path) { throw "Release target already exists: $path" }
}
if (-not (Test-Path -LiteralPath (Join-Path $projectRoot "frontend\dist\index.html"))) {
    throw "Production frontend is missing. Run npm run build in frontend first."
}

New-Item -ItemType Directory -Path $destinationRoot -Force | Out-Null
git -C $projectRoot archive --format=zip --output=$sourceArchive HEAD
if ($LASTEXITCODE -ne 0) { throw "Git source archive failed." }
New-Item -ItemType Directory -Path $stage | Out-Null
Expand-Archive -LiteralPath $sourceArchive -DestinationPath $stage
Copy-Item -LiteralPath (Join-Path $projectRoot "frontend\dist") -Destination (Join-Path $stage "frontend\dist") -Recurse
Compress-Archive -Path (Join-Path $stage "*") -DestinationPath $releaseArchive -CompressionLevel Optimal

$lines = foreach ($path in @($sourceArchive, $releaseArchive)) {
    $file = Get-Item -LiteralPath $path
    $hash = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLower()
    "$hash  $($file.Name)  $($file.Length) bytes"
}
$lines | Set-Content -LiteralPath $checksumFile -Encoding utf8
Write-Host "Release folder: $stage" -ForegroundColor Green
Write-Host "Release ZIP:    $releaseArchive" -ForegroundColor Green
Write-Host "Checksums:      $checksumFile" -ForegroundColor Green
