@echo off
REM Smart Parking System - Simple Setup Script for Windows

echo 🚗 Smart Parking System - Quick Setup
echo =====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Python is not installed. Please install Python 3.9+ first.
    echo    Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python found
python --version

REM Create virtual environment
echo.
echo 📦 Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo 📦 Activating virtual environment...
call venv\Scripts\activate.bat

echo ✅ Virtual environment created and activated

REM Install Python dependencies
echo.
echo 📦 Installing Python dependencies...
echo    This may take a few minutes...
pip install -r requirements.txt

if %ERRORLEVEL% EQU 0 (
    echo ✅ Python dependencies installed
) else (
    echo ⚠️ Some dependencies may have issues, but continuing...
)

REM Copy environment file
echo.
if not exist .env (
    if exist .env.example (
        copy .env.example .env >nul
        echo ✅ Environment file created (.env)
        echo ⚠️  Please edit .env file with your configurations
    ) else (
        echo ⚠️ .env.example not found, skipping environment file creation
    )
) else (
    echo ℹ️  .env file already exists
)

echo.
echo 🎉 Backend setup complete!
echo.
echo To start the backend:
echo 1. Activate virtual environment: venv\Scripts\activate.bat
echo 2. Run: python smart_parking_backend.py
echo.
echo The backend will be available at: http://localhost:5000
echo.
pause
