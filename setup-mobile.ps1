# PowerShell script to setup Smart Parking Mobile App

Write-Host "📱 Smart Parking Mobile App - Setup" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan

# Check if Node.js is installed
try {
    $nodeVersion = node --version 2>$null
    Write-Host "✅ Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js is not installed. Please install Node.js 16+ first." -ForegroundColor Red
    Write-Host "   Download from: https://nodejs.org/" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if we're in the right directory
if (-not (Test-Path "smart_parking_mobile.js")) {
    Write-Host "❌ smart_parking_mobile.js not found in current directory" -ForegroundColor Red
    Write-Host "   Please run this script from the parking system directory" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "🚀 Setting up mobile app..." -ForegroundColor Yellow

# Create mobile app directory
$mobileDir = "SmartParkingApp"
if (Test-Path $mobileDir) {
    Write-Host "📁 Mobile app directory already exists" -ForegroundColor Blue
} else {
    Write-Host "📁 Creating mobile app directory..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Name $mobileDir | Out-Null
}

# Change to mobile directory
Set-Location $mobileDir

# Create package.json if it doesn't exist
if (-not (Test-Path "package.json")) {
    Write-Host "📦 Creating package.json..." -ForegroundColor Yellow
    
    $packageJson = @"
{
  "name": "smart-parking-app",
  "version": "1.0.0",
  "main": "node_modules/expo/AppEntry.js",
  "scripts": {
    "start": "expo start",
    "android": "expo start --android",
    "ios": "expo start --ios",
    "web": "expo start --web"
  },
  "dependencies": {
    "expo": "~49.0.15",
    "expo-status-bar": "~1.6.0",
    "react": "18.2.0",
    "react-native": "0.72.6",
    "@react-navigation/native": "^6.1.9",
    "@react-navigation/bottom-tabs": "^6.5.11",
    "@expo/vector-icons": "^13.0.0",
    "react-native-screens": "~3.22.0",
    "react-native-safe-area-context": "4.6.3"
  },
  "devDependencies": {
    "@babel/core": "^7.20.0"
  },
  "private": true
}
"@
    
    $packageJson | Out-File -FilePath "package.json" -Encoding UTF8
}

# Create app.json if it doesn't exist
if (-not (Test-Path "app.json")) {
    Write-Host "⚙️ Creating app.json..." -ForegroundColor Yellow
    
    $appJson = @"
{
  "expo": {
    "name": "Smart Parking",
    "slug": "smart-parking",
    "version": "1.0.0",
    "orientation": "portrait",
    "icon": "./assets/icon.png",
    "userInterfaceStyle": "light",
    "splash": {
      "image": "./assets/splash.png",
      "resizeMode": "contain",
      "backgroundColor": "#ffffff"
    },
    "platforms": [
      "ios",
      "android",
      "web"
    ]
  }
}
"@
    
    $appJson | Out-File -FilePath "app.json" -Encoding UTF8
}

# Copy mobile app code
Write-Host "📱 Copying mobile app code..." -ForegroundColor Yellow
Copy-Item "..\smart_parking_mobile.js" "App.js" -Force

# Install dependencies
Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
Write-Host "   This may take a few minutes..." -ForegroundColor Gray

npm install

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Dependencies installed successfully" -ForegroundColor Green
} else {
    Write-Host "⚠️ Some dependencies may have warnings, but setup should work" -ForegroundColor Yellow
}

# Install Expo CLI globally if not present
Write-Host "🔧 Checking Expo CLI..." -ForegroundColor Yellow
try {
    $expoVersion = npx expo --version 2>$null
    Write-Host "✅ Expo CLI found: $expoVersion" -ForegroundColor Green
} catch {
    Write-Host "📦 Installing Expo CLI globally..." -ForegroundColor Yellow
    npm install -g @expo/cli
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Expo CLI installed" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Could not install Expo CLI globally. You can use 'npx expo' instead" -ForegroundColor Yellow
    }
}

# Get computer IP address for configuration
Write-Host ""
Write-Host "🌐 Network Configuration:" -ForegroundColor Cyan
try {
    # Try to get WiFi adapter IP first
    $ipAddress = $null
    $wifiAdapter = Get-NetAdapter -Name "*Wi-Fi*" -ErrorAction SilentlyContinue | Where-Object { $_.Status -eq "Up" } | Select-Object -First 1
    if ($wifiAdapter) {
        $ipAddress = (Get-NetIPAddress -InterfaceIndex $wifiAdapter.InterfaceIndex -AddressFamily IPv4 -ErrorAction SilentlyContinue | Where-Object { $_.PrefixOrigin -eq "Dhcp" }).IPAddress
    }
    
    # Fallback to any private IP
    if (-not $ipAddress) {
        $allIPs = Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue | Where-Object { 
            ($_.IPAddress -like "192.168.*") -or 
            ($_.IPAddress -like "10.*") -or 
            ($_.IPAddress -like "172.1[6-9].*") -or 
            ($_.IPAddress -like "172.2[0-9].*") -or 
            ($_.IPAddress -like "172.3[0-1].*")
        }
        $ipAddress = $allIPs | Select-Object -First 1 | Select-Object -ExpandProperty IPAddress
    }
    
    if ($ipAddress) {
        Write-Host "   📍 Your computer's IP: $ipAddress" -ForegroundColor White
        Write-Host "   📱 Mobile devices should use: http://${ipAddress}:5000/api" -ForegroundColor White
        
        # Update the API URL in App.js
        $appContent = Get-Content "App.js" -Raw
        $updatedContent = $appContent -replace "const API_BASE_URL = 'http://localhost:5000/api';", "const API_BASE_URL = 'http://${ipAddress}:5000/api';"
        $updatedContent | Out-File "App.js" -Encoding UTF8
        
        Write-Host "   ✅ Updated App.js with your computer's IP address" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️ Could not detect IP address automatically" -ForegroundColor Yellow
        Write-Host "   📝 You may need to manually update API_BASE_URL in App.js" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ⚠️ Could not detect network configuration" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎉 Mobile app setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📱 Next steps:" -ForegroundColor Cyan
Write-Host "1. Install 'Expo Go' app on your phone (App Store/Google Play)" -ForegroundColor White
Write-Host "2. Ensure your phone and computer are on the same WiFi network" -ForegroundColor White
Write-Host "3. Start the backend: cd .. && .\start.ps1" -ForegroundColor White
Write-Host "4. Start the mobile app: npm start" -ForegroundColor White
Write-Host "5. Scan the QR code with Expo Go app" -ForegroundColor White
Write-Host ""
Write-Host "🌐 Test backend connection:" -ForegroundColor Cyan
if ($ipAddress) {
    Write-Host "   Open browser on phone: http://${ipAddress}:5000" -ForegroundColor White
} else {
    Write-Host "   Find your IP with 'ipconfig' and test: http://YOUR-IP:5000" -ForegroundColor White
}

Write-Host ""
Read-Host "Press Enter to continue"
