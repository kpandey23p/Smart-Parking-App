# PowerShell start script for Smart Parking System

Write-Host "🚗 Starting Smart Parking System Backend..." -ForegroundColor Cyan

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "❌ Virtual environment not found. Please run setup.ps1 first." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Activate virtual environment
Write-Host "📦 Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  .env file not found. Copying from .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
}

Write-Host "🚀 Starting backend server..." -ForegroundColor Green
Write-Host "📊 Dashboard will be available at: http://localhost:5000" -ForegroundColor Cyan
Write-Host "🔧 API documentation at: http://localhost:5000/api/status" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

python smart_parking_backend.py
