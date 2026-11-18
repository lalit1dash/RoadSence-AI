@echo off
echo ========================================================
echo  RoadSense Backend API - Starting on http://localhost:8000
echo ========================================================
cd /d "%~dp0backend"
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
pause
