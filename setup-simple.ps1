# Simple PowerShell setup script for Smart Parking System
param(
    [switch]$SkipVenv
)

Write-Host "🚗 Smart Parking System - Quick Setup" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# Check if Python is installed
$pythonCheck = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCheck) {
    Write-Host "❌ Python is not installed. Please install Python 3.9+ first." -ForegroundColor Red
    Write-Host "   Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

$pythonVersion = python --version
Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green

if (-not $SkipVenv) {
    # Create virtual environment
    Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    
    # Activate virtual environment
    Write-Host "📦 Activating virtual environment..." -ForegroundColor Yellow
    $activateScript = ".\venv\Scripts\Activate.ps1"
    if (Test-Path $activateScript) {
        & $activateScript
        Write-Host "✅ Virtual environment created and activated" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Virtual environment created but activation script not found" -ForegroundColor Yellow
        Write-Host "   You may need to activate manually: .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
    }
}

# Install Python dependencies
Write-Host "📦 Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Python dependencies installed" -ForegroundColor Green
} else {
    Write-Host "⚠️ Some dependencies may have issues, but continuing..." -ForegroundColor Yellow
}

# Copy environment file
if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "✅ Environment file created (.env)" -ForegroundColor Green
        Write-Host "⚠️  Please edit .env file with your configurations" -ForegroundColor Yellow
    } else {
        Write-Host "⚠️ .env.example not found, skipping environment file creation" -ForegroundColor Yellow
    }
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
