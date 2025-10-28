@echo off
REM SmartMoneyTracker Web Interface Startup Script for Windows

echo ======================================
echo   SmartMoneyTracker Web Interface
echo ======================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed. Please install Python 3.9 or higher.
    pause
    exit /b 1
)

REM Check if required packages are installed
echo Checking dependencies...
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo Warning: Flask is not installed. Installing dependencies...
    pip install -r requirements.txt
)

echo.
echo Starting SmartMoneyTracker Web Server...
echo.
echo Server will be available at: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.
echo ======================================
echo.

REM Start the Flask application
python app.py

pause
