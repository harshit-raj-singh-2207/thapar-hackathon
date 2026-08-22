@echo off
echo ===================================================
echo   Starting NIVARA Backend and Frontend Servers
echo ===================================================
echo.
echo Starting FastAPI Backend on http://localhost:8001 ...
start "NIVARA Backend (FastAPI)" cmd /k "cd /d %~dp0backend && python run.py"

echo Starting Expo Frontend ...
start "NIVARA Frontend (Expo)" cmd /k "cd /d %~dp0frontend && npx --yes node@18 node_modules/expo/bin/cli start --web"

echo.
echo Both backend and frontend windows have been opened!
