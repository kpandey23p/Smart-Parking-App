# PowerShell script to start Smart Parking Mobile App

Write-Host "📱 Starting Smart Parking Mobile App..." -ForegroundColor Cyan

# Check if mobile app directory exists
if (-not (Test-Path "SmartParkingApp")) {
    Write-Host "❌ Mobile app not found. Please run setup-mobile.ps1 first." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Change to mobile app directory
Set-Location "SmartParkingApp"

# Check if node_modules exists
if (-not (Test-Path "node_modules")) {
    Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
    npm install
}

# Check if backend is running
Write-Host "🔍 Checking backend connection..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/api/status" -UseBasicParsing -TimeoutSec 5
    Write-Host "✅ Backend is running" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Backend not responding. Make sure to start the backend first:" -ForegroundColor Yellow
    Write-Host "   cd .. && .\start.ps1" -ForegroundColor White
    Write-Host ""
    Write-Host "Press Ctrl+C to cancel, or any key to continue anyway..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

Write-Host ""
Write-Host "🚀 Starting mobile app..." -ForegroundColor Green
Write-Host "📱 Instructions:" -ForegroundColor Cyan
Write-Host "1. A QR code will appear" -ForegroundColor White
Write-Host "2. Open 'Expo Go' app on your phone" -ForegroundColor White
Write-Host "3. Scan the QR code" -ForegroundColor White
Write-Host "4. The app will load on your phone" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

# Start the Expo development server
npm start
