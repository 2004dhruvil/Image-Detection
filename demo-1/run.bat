@echo off
echo --- Image Detection Demo-1 Setup ---

REM Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    pause
    exit /b
)

REM Install dependencies
echo [INFO] Installing/Updating dependencies from requirements.txt...
pip install -r requirements.txt

REM Run the app
echo [INFO] Starting Flask Application...
python app.py

pause
