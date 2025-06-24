@echo off
REM Quick setup script for Smart Parking System (Windows)

echo 🚗 Smart Parking System - Quick Setup
echo =====================================

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Python is not installed. Please install Python 3.9+ first.
    pause
    exit /b 1
)

echo ✅ Python found

REM Create virtual environment
echo 📦 Creating virtual environment...
python -m venv venv

REM Activate virtual environment
call venv\Scripts\activate.bat

echo ✅ Virtual environment created and activated

REM Install Python dependencies
echo 📦 Installing Python dependencies...
pip install -r requirements.txt

echo ✅ Python dependencies installed

REM Copy environment file
if not exist .env (
    copy .env.example .env
    echo ✅ Environment file created (.env)
    echo ⚠️  Please edit .env file with your configurations
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
pause
