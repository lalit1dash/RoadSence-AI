@echo off
echo ========================================================
echo  RoadSense Frontend - Starting on http://localhost:5173
echo ========================================================
cd /d "%~dp0frontend"
npm run dev
pause
