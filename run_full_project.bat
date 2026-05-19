@echo off
setlocal
cd /d "%~dp0"

echo =========================================
echo Starting full project: AI Core + Backend + Frontend
echo =========================================
echo.

rem Prepare Python venv for ai_core
if not exist "ai_core\venv\Scripts\activate.bat" (
    echo Creating Python virtual environment...
    python -m venv ai_core\venv
)

rem Start ai_core service
start "AI Core" cmd /k "pushd "%~dp0ai_core" && call venv\Scripts\activate.bat && python server.py"

rem Start Express backend service
start "Backend" cmd /k "pushd "%~dp0backend" && if not exist node_modules npm install && npm run dev"

rem Start React frontend service
start "Frontend" cmd /k "pushd "%~dp0frontend" && if not exist node_modules npm install && npm run dev"

echo.
echo All services are launching in separate terminals.
echo Frontend: http://localhost:5173
echo Backend AI Core: http://localhost:5000
echo Express backend: http://localhost:3001
echo.
echo Note: wait for each service to finish starting before opening the browser.
pause
