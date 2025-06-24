# 📱 Smart Parking Mobile App - Setup Guide

## Overview

The mobile app is built with **React Native + Expo**, making it easy to run on both iOS and Android devices without needing Android Studio or Xcode.

## 🚀 Quick Setup

### 1. Prerequisites
- **Node.js 16+** installed
- **Expo CLI** (we'll install this)
- **Expo Go app** on your phone (from App Store/Google Play)

### 2. Setup Steps

1. **Navigate to your project folder:**
   ```powershell
   cd "c:\parking system"
   ```

2. **Install Node.js dependencies:**
   ```powershell
   npm install
   ```

3. **Install Expo CLI globally:**
   ```powershell
   npm install -g expo-cli
   # or alternatively:
   npm install -g @expo/cli
   ```

4. **Create the React Native app structure:**
   ```powershell
   # Create a new Expo app
   npx create-expo-app SmartParkingApp --template blank
   cd SmartParkingApp
   ```

5. **Replace the default App.js with our mobile app:**
   ```powershell
   # Copy our mobile app code
   Copy-Item "..\smart_parking_mobile.js" "App.js" -Force
   ```

6. **Install additional dependencies:**
   ```powershell
   npm install @react-navigation/native @react-navigation/bottom-tabs
   npm install react-native-screens react-native-safe-area-context
   npx expo install react-native-screens react-native-safe-area-context
   ```

### 3. Start the Mobile App

```powershell
npm start
# or
npx expo start
```

### 4. Run on Your Device

1. **Install Expo Go** on your phone:
   - **iOS**: Download from App Store
   - **Android**: Download from Google Play Store

2. **Scan the QR code** that appears in your terminal/browser

3. **Alternative**: Use device simulators:
   ```powershell
   # For Android emulator (if you have Android Studio)
   npm run android
   
   # For iOS simulator (if you have Xcode on Mac)
   npm run ios
   
   # For web browser
   npm run web
   ```

## 📱 Mobile App Features

When the app loads, you'll see three main screens:

### 🏠 Dashboard Tab
- Real-time parking status
- Available spots counter
- Current pricing
- Interactive parking grid
- Refresh functionality

### 🔍 Find Parking Tab  
- AI-powered spot recommendations
- Scoring system for best spots
- Navigation integration
- Confidence ratings

### 📊 Analytics Tab
- 24-hour pricing history
- Occupancy trends
- Visual charts
- AI insights

## 🔧 Configuration

### Update API Connection

If your backend is running on a different IP or port, update the API URL:

```javascript
// In App.js (smart_parking_mobile.js), line ~22:
const API_BASE_URL = 'http://YOUR-COMPUTER-IP:5000/api';
```

**To find your computer's IP:**
```powershell
ipconfig
# Look for "IPv4 Address" under your network adapter
```

### Network Requirements

- **Same WiFi**: Ensure your phone and computer are on the same WiFi network
- **Firewall**: Windows might block connections - allow Python/Node.js through firewall
- **Port Access**: Ensure port 5000 is accessible

## 🧪 Testing the Connection

1. **Start the backend first:**
   ```powershell
   .\start.ps1
   ```

2. **Test API access from mobile:**
   - Open browser on phone
   - Go to `http://YOUR-COMPUTER-IP:5000`
   - You should see the web dashboard

3. **Then start mobile app:**
   ```powershell
   cd SmartParkingApp
   npm start
   ```

## ⚠️ Troubleshooting

### 1. "Network Error" in mobile app
```powershell
# Check if backend is running
curl http://localhost:5000/api/status

# Check computer's IP address
ipconfig

# Update API_BASE_URL in App.js to use computer's IP instead of localhost
```

### 2. "Module not found" errors
```powershell
# Clear cache and reinstall
npm install
npx expo install --fix
```

### 3. "Expo CLI not found"
```powershell
# Install globally
npm install -g @expo/cli
# or
yarn global add @expo/cli
```

### 4. App won't scan QR code
- Ensure phone and computer are on same WiFi
- Try typing the URL manually in Expo Go
- Use `npx expo start --tunnel` for external access

## 🚀 Alternative: Quick Mobile Setup

If you want to get started immediately without creating a new Expo project:

1. **Create a minimal React Native setup:**

```powershell
# Create app.json
@"
{
  "expo": {
    "name": "Smart Parking",
    "slug": "smart-parking",
    "version": "1.0.0",
    "platforms": ["ios", "android", "web"],
    "sdkVersion": "49.0.0"
  }
}
"@ | Out-File -FilePath "app.json" -Encoding UTF8

# Rename smart_parking_mobile.js to App.js
Copy-Item "smart_parking_mobile.js" "App.js"

# Start with Expo
npx expo start
```

## 📋 File Structure for Mobile App

```
SmartParkingApp/
├── App.js                 # Main app file (from smart_parking_mobile.js)
├── package.json           # Dependencies
├── app.json              # Expo configuration
└── node_modules/         # Installed packages
```

## 🎯 Next Steps

1. **Get backend running** (`.\start.ps1`)
2. **Set up mobile app** (follow steps above)
3. **Test connection** between mobile and backend
4. **Customize the UI** and features
5. **Deploy to app stores** (when ready)

The mobile app provides a native mobile experience for your smart parking system with real-time updates and intuitive navigation!
