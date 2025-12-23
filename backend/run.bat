@echo off
echo ==========================================
echo      Starting Self Xerox Kiosk System
echo ==========================================

cd /d "%~dp0"

echo [1/4] Installing/Verifying Dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Error installing dependencies!
    pause
    exit /b %errorlevel%
)

echo.
echo [2/4] Setting up Database (if needed)...
python setup_postgres.py

echo.
echo [3/4] Seeding Default Data...
python seed_db.py

echo.
echo [4/4] Starting Server...
echo.
echo    Active Interfaces:
echo    - Kiosk: http://localhost:8000/kiosk/
echo    - Admin: http://localhost:8000/admin/  (Login: admin/password)
echo    - Mobile: http://localhost:8000/mobile/upload.html
echo.

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
pause
