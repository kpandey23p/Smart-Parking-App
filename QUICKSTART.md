# 🚗 Smart Parking System - Quick Start Guide

## Prerequisites

Before you begin, make sure you have:
- **Python 3.9+** installed
- **Node.js 16+** installed (for mobile app)
- **Git** installed (optional)

**📌 Note**: No API keys required! The system works perfectly in simulation mode.

## 🚀 Quick Start (5 minutes)

### Option 1: PowerShell Setup (Recommended for Windows)

1. **Open PowerShell as Administrator** in your project directory
2. **Run the setup script:**
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   .\setup.ps1
   ```
3. **Start the backend:**
   ```powershell
   .\start.ps1
   ```

### Option 2: Manual Setup

1. **Create and activate virtual environment:**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

2. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Copy environment file:**
   ```powershell
   Copy-Item .env.example .env
   ```

4. **Start the backend:**
   ```powershell
   python smart_parking_backend.py
   ```

## 🌐 Access the System

After starting the backend, you can access:

- **Web Dashboard**: http://localhost:5000
- **API Status**: http://localhost:5000/api/status
- **API Documentation**: All endpoints listed in README.md

## 📱 Mobile App Setup (Optional)

### Quick Mobile Setup:

1. **Run the mobile setup script:**
   ```powershell
   .\setup-mobile.ps1
   ```

2. **Start the mobile app:**
   ```powershell
   .\start-mobile.ps1
   ```

3. **Install Expo Go** on your phone (App Store/Google Play)

4. **Scan the QR code** that appears in your terminal

### Manual Mobile Setup:

1. **Install dependencies:**
   ```powershell
   npm install
   ```

2. **Install Expo CLI globally:**
   ```powershell
   npm install -g expo-cli
   ```

3. **Start the mobile app:**
   ```powershell
   npm start
   ```

4. **Run on device:**
   - Install "Expo Go" app on your phone
   - Scan the QR code from terminal

## 🎯 What You'll See

### Web Dashboard Features:
- ✅ Real-time parking spot status
- 📊 Occupancy statistics
- 💰 Dynamic pricing display
- 🔄 Auto-refresh every 10 seconds
- 🎮 Manual update controls

### Mobile App Features:
- 📱 Native mobile interface
- 🎯 AI-powered spot recommendations
- 📈 Analytics and pricing trends
- 🚗 Interactive parking grid

## 🧪 Test the System

1. **Check API endpoints:**
   ```powershell
   # Get status
   curl http://localhost:5000/api/status
   
   # Trigger update
   curl -X POST http://localhost:5000/api/update
   
   # Find parking
   curl http://localhost:5000/api/find-parking
   ```

2. **Simulate parking changes:**
   - Click "Update Detection" in web dashboard
   - Watch parking spots change color
   - Observe dynamic pricing adjustments

## 🔧 Configuration

Edit the `.env` file to customize:
- Database settings
- API configuration  
- Computer vision parameters
- Pricing algorithms

**🤖 Want AI features?** See `AI_INTEGRATION.md` for OpenAI integration (optional).

## 📚 Next Steps

1. **Explore the code** in `smart_parking_backend.py`
2. **Customize the UI** in the HTML dashboard
3. **Add real camera integration** (replace simulation)
4. **Deploy to production** using Docker
5. **Extend with more features**

## ⚠️ Troubleshooting

### Common Issues:

1. **"Module not found" errors:**
   ```powershell
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

2. **Port 5000 already in use:**
   ```powershell
   netstat -ano | findstr :5000
   # Kill the process using the port
   ```

3. **Database issues:**
   ```powershell
   Remove-Item parking.db -ErrorAction SilentlyContinue
   # Restart the application
   ```

4. **PowerShell execution policy:**
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

## 🎉 You're Ready!

Your smart parking system is now running! The system includes:
- **🎯 Intelligent simulation** (no API keys needed)
- **🤖 Multi-agent architecture** with AI-style decision making
- **💰 Dynamic pricing algorithms** 
- **📊 Predictive analytics** using mathematical models
- **📱 Cross-platform mobile app**

Start exploring and customizing your intelligent parking management system!

**🚀 Next Steps:**
- Explore the web dashboard and mobile app
- Check out `AI_INTEGRATION.md` for optional AI enhancements
- See `DEVELOPMENT.md` for customization options
