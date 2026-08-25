@echo off
setlocal
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\verify.ps1"
echo.
if errorlevel 1 (
  echo TerraFly verification FAILED. Read the first red error above.
) else (
  echo TerraFly verification PASSED.
)
echo Press any key to close this checker.
pause >nul
