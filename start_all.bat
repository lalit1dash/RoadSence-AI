@echo off
echo ===================================================================
echo  Starting RoadSense - AI Road Damage Detection and Risk Prediction
echo ===================================================================

echo [1/2] Launching Backend API on http://localhost:8000 ...
start "RoadSense Backend" cmd /k "cd /d %~dp0backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

timeout /t 3 /nobreak >nul

echo [2/2] Launching Frontend on http://localhost:5173 ...
start "RoadSense Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo Both services are booting up!
echo - Frontend: http://localhost:5173
echo - Backend API Docs: http://localhost:8000/docs
echo ===================================================================
pause
