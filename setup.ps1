# PowerShell setup script for Smart Parking System

Write-Host "🚗 Smart Parking System - Quick Setup" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# Check if Python is installed
try {
    $pythonVersion = python --version 2>$null
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python is not installed. Please install Python 3.9+ first." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Create virtual environment
Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
python -m venv venv

# Activate virtual environment
Write-Host "📦 Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

Write-Host "✅ Virtual environment created and activated" -ForegroundColor Green

# Install Python dependencies
Write-Host "📦 Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host "✅ Python dependencies installed" -ForegroundColor Green

# Copy environment file
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "✅ Environment file created (.env)" -ForegroundColor Green
    Write-Host "⚠️  Please edit .env file with your configurations" -ForegroundColor Yellow
} else {
    Write-Host "ℹ️  .env file already exists" -ForegroundColor Blue
}

Write-Host ""
Write-Host "🎉 Backend setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "To start the backend:" -ForegroundColor Cyan
Write-Host "1. Activate virtual environment: .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "2. Run: python smart_parking_backend.py" -ForegroundColor White
Write-Host ""
Write-Host "The backend will be available at: http://localhost:5000" -ForegroundColor Green

Read-Host "Press Enter to continue"
