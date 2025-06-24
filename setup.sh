#!/bin/bash
# Quick setup script for Smart Parking System

echo "🚗 Smart Parking System - Quick Setup"
echo "====================================="

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed. Please install Python 3.9+ first."
    exit 1
fi

echo "✅ Python found"

# Create virtual environment
echo "📦 Creating virtual environment..."
python -m venv venv

# Activate virtual environment (Windows)
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

echo "✅ Virtual environment created and activated"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

echo "✅ Python dependencies installed"

# Copy environment file
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Environment file created (.env)"
    echo "⚠️  Please edit .env file with your configurations"
else
    echo "ℹ️  .env file already exists"
fi

echo ""
echo "🎉 Backend setup complete!"
echo ""
echo "To start the backend:"
echo "1. Activate virtual environment: source venv/bin/activate (Linux/Mac) or venv\\Scripts\\activate (Windows)"
echo "2. Run: python smart_parking_backend.py"
echo ""
echo "The backend will be available at: http://localhost:5000"
