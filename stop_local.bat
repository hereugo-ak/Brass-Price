@echo off
REM ===========================================================================
REM  Brass Guard — stop anything listening on 8000 or 8080
REM ===========================================================================
setlocal enabledelayedexpansion
set FOUND=0

for %%P in (8000 8080) do (
  for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%%P " ^| findstr LISTENING') do (
    echo Stopping process %%a on port %%P
    taskkill /F /PID %%a >nul 2>&1
    set FOUND=1
  )
)

if "!FOUND!"=="0" (
  echo Nothing was listening on 8000 or 8080.
) else (
  echo Done.
)
ping -n 4 127.0.0.1 >nul
exit /b 0
