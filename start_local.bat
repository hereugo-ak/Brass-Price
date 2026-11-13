@echo off
REM ===========================================================================
REM  Brass Guard — start backend and frontend on localhost
REM  Double-click this file. Two windows open; close both to stop.
REM ===========================================================================
setlocal
cd /d "%~dp0"

set PY=python
where python >nul 2>&1 || set PY=py

echo.
echo   Brass Guard
echo   -----------
echo   Checking Python...
%PY% --version || goto :nopython

if not exist "brass.db" (
  echo   First run: creating the database...
  %PY% -m app.cli init
)

echo   Starting the backend on http://127.0.0.1:8000
start "Brass Guard API" cmd /k %PY% -m uvicorn app.api:app --host 127.0.0.1 --port 8000

echo   Starting the page on http://127.0.0.1:8080
start "Brass Guard Page" cmd /k %PY% -m http.server 8080 --bind 127.0.0.1

echo   Waiting for both to come up...
ping -n 7 127.0.0.1 >nul

start "" "http://127.0.0.1:8080/Castle_Quote_Checker.html"

echo.
echo   Backend  : http://127.0.0.1:8000        (API docs at /docs)
echo   Frontend : http://127.0.0.1:8080/Castle_Quote_Checker.html
echo.
echo   The two black windows must stay open while you use it.
echo   To stop: close those two windows, or run stop_local.bat
echo.
pause
exit /b 0

:nopython
echo.
echo   Python was not found on PATH.
echo   Install Python 3.11+ from python.org, tick "Add Python to PATH",
echo   then run this file again.
echo.
pause
exit /b 1
