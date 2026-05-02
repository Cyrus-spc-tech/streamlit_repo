@echo off
title ClassMind Server Starter
echo ---------------------------------------------------
echo ClassMind: Starting Backend Server...
echo ---------------------------------------------------

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python from python.org
    pause
    exit /b
)

echo [1/3] Checking/Installing requirements...
python -m pip install fastapi uvicorn[standard] python-dotenv python-multipart aiosmtplib pydantic google-auth --quiet

echo [2/3] Starting Server on http://localhost:8000
echo (Keep this window open while using the app)
echo ---------------------------------------------------

:: Run uvicorn using the module flag to avoid PATH issues
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Server failed to start. 
    echo Try running: pip install -r requirements.txt
    pause
)
