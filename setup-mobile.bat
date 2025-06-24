@echo off
rem Smart Parking Mobile App - Setup (Batch Version)
echo 📱 Smart Parking Mobile App - Setup
echo ====================================

rem Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed. Please install Node.js 16+ first.
    echo    Download from: https://nodejs.org/
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('node --version 2^>nul') do set NODE_VERSION=%%i
echo ✅ Node.js found: %NODE_VERSION%

rem Check if we're in the right directory
if not exist "smart_parking_mobile.js" (
    echo ❌ smart_parking_mobile.js not found in current directory
    echo    Please run this script from the parking system directory
    pause
    exit /b 1
)

echo.
echo 🚀 Setting up mobile app...

rem Create mobile app directory
set MOBILE_DIR=SmartParkingApp
if not exist "%MOBILE_DIR%" (
    echo 📁 Creating mobile app directory...
    mkdir "%MOBILE_DIR%"
) else (
    echo 📁 Mobile app directory already exists
)

rem Change to mobile directory
cd "%MOBILE_DIR%"

rem Create package.json if it doesn't exist
if not exist "package.json" (
    echo 📦 Creating package.json...
    (
        echo {
        echo   "name": "smart-parking-app",
        echo   "version": "1.0.0",
        echo   "main": "node_modules/expo/AppEntry.js",
        echo   "scripts": {
        echo     "start": "expo start",
        echo     "android": "expo start --android",
        echo     "ios": "expo start --ios",
        echo     "web": "expo start --web"
        echo   },
        echo   "dependencies": {
        echo     "expo": "~49.0.15",
        echo     "expo-status-bar": "~1.6.0",
        echo     "react": "18.2.0",
        echo     "react-native": "0.72.6",
        echo     "@react-navigation/native": "^6.1.9",
        echo     "@react-navigation/bottom-tabs": "^6.5.11",
        echo     "@expo/vector-icons": "^13.0.0",
        echo     "react-native-screens": "~3.22.0",
        echo     "react-native-safe-area-context": "4.6.3"
        echo   },
        echo   "devDependencies": {
        echo     "@babel/core": "^7.20.0"
        echo   },
        echo   "private": true
        echo }
    ) > package.json
)

rem Create app.json if it doesn't exist
if not exist "app.json" (
    echo ⚙️ Creating app.json...
    (
        echo {
        echo   "expo": {
        echo     "name": "Smart Parking",
        echo     "slug": "smart-parking",
        echo     "version": "1.0.0",
        echo     "orientation": "portrait",
        echo     "icon": "./assets/icon.png",
        echo     "userInterfaceStyle": "light",
        echo     "splash": {
        echo       "image": "./assets/splash.png",
        echo       "resizeMode": "contain",
        echo       "backgroundColor": "#ffffff"
        echo     },
        echo     "platforms": [
        echo       "ios",
        echo       "android",
        echo       "web"
        echo     ]
        echo   }
        echo }
    ) > app.json
)

rem Copy mobile app code
echo 📱 Copying mobile app code...
copy "..\smart_parking_mobile.js" "App.js" /Y >nul

rem Install dependencies
echo 📦 Installing dependencies...
echo    This may take a few minutes...
call npm install

if errorlevel 1 (
    echo ⚠️ Some dependencies may have warnings, but setup should work
) else (
    echo ✅ Dependencies installed successfully
)

rem Check Expo CLI
echo 🔧 Checking Expo CLI...
npx expo --version >nul 2>&1
if errorlevel 1 (
    echo 📦 Installing Expo CLI...
    call npm install -g @expo/cli
    if errorlevel 1 (
        echo ⚠️ Could not install Expo CLI globally. You can use 'npx expo' instead
    ) else (
        echo ✅ Expo CLI installed
    )
) else (
    for /f "tokens=*" %%i in ('npx expo --version 2^>nul') do set EXPO_VERSION=%%i
    echo ✅ Expo CLI found: %EXPO_VERSION%
)

echo.
echo 🌐 Network Configuration:
rem Get IP address (simplified approach)
for /f "tokens=2 delims=:" %%i in ('ipconfig ^| findstr /i "IPv4"') do (
    set IP_TEMP=%%i
    call set IP_ADDRESS=%%IP_TEMP: =%%
    goto :found_ip
)
:found_ip

if defined IP_ADDRESS (
    echo    📍 Your computer's IP: %IP_ADDRESS%
    echo    📱 Mobile devices should use: http://%IP_ADDRESS%:5000/api
    
    rem Update API URL in App.js (simplified)
    powershell -Command "(Get-Content 'App.js') -replace 'const API_BASE_URL = ''http://localhost:5000/api'';', 'const API_BASE_URL = ''http://%IP_ADDRESS%:5000/api'';' | Out-File 'App.js' -Encoding UTF8"
    echo    ✅ Updated App.js with your computer's IP address
) else (
    echo    ⚠️ Could not detect IP address automatically
    echo    📝 You may need to manually update API_BASE_URL in App.js
)

echo.
echo 🎉 Mobile app setup complete!
echo.
echo 📱 Next steps:
echo 1. Install 'Expo Go' app on your phone (App Store/Google Play^)
echo 2. Ensure your phone and computer are on the same WiFi network
echo 3. Start the backend: cd .. ^&^& setup-basic.bat
echo 4. Start the mobile app: npm start
echo 5. Scan the QR code with Expo Go app
echo.
echo 🌐 Test backend connection:
if defined IP_ADDRESS (
    echo    Open browser on phone: http://%IP_ADDRESS%:5000
) else (
    echo    Find your IP with 'ipconfig' and test: http://YOUR-IP:5000
)

echo.
pause
