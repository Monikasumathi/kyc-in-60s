#!/bin/bash

# KYC-in-60s Setup Script
# This script sets up the complete development environment

set -e

echo "╔══════════════════════════════════════════════════════════╗"
echo "║         KYC-in-60s Setup Script                         ║"
echo "║         Setting up backend and frontend...              ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed. Please install Node.js 16 or higher."
    exit 1
fi

echo "✅ Python and Node.js found"
echo ""

# Backend Setup
echo "📦 Setting up Backend..."
echo "------------------------"

cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip

# Install cmake first (needed for dlib)
echo "Installing cmake..."
pip install cmake

# Try to install dlib (needed for face-recognition)
echo "Installing dlib (this may take a few minutes)..."
if pip install dlib; then
    echo "✅ dlib installed successfully"
else
    echo "⚠️  dlib installation failed. Trying alternative method..."
    # On macOS, try with homebrew's cmake
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install cmake
    fi
    pip install dlib || echo "❌ dlib installation failed. Face matching may not work."
fi

# Install other dependencies
echo "Installing remaining dependencies..."
pip install -r requirements.txt || {
    echo "⚠️  Some packages failed to install. Trying without face-recognition..."
    # Create temp requirements without face-recognition
    grep -v "face-recognition" requirements.txt > requirements.temp.txt
    pip install -r requirements.temp.txt
    rm requirements.temp.txt
    echo "⚠️  Face recognition not installed. Face matching feature will be disabled."
}

# Install Tesseract OCR if not present (macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    if ! command -v tesseract &> /dev/null; then
        echo "📦 Installing Tesseract OCR..."
        brew install tesseract
    fi
fi

# Create necessary directories
mkdir -p uploads logs

# Copy environment file
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please update .env file with your configuration"
fi

echo "✅ Backend setup complete!"
echo ""

cd ..

# Frontend Setup
echo "📦 Setting up Frontend..."
echo "-------------------------"

cd frontend

# Install Node dependencies
echo "Installing Node.js dependencies..."
npm install --silent

# Copy environment file
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
fi

echo "✅ Frontend setup complete!"
echo ""

cd ..

# Final instructions
echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║                 Setup Complete! 🎉                       ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "To start the application:"
echo ""
echo "Terminal 1 (Backend):"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  python run.py"
echo ""
echo "Terminal 2 (Frontend):"
echo "  cd frontend"
echo "  npm run dev"
echo ""
echo "Then open http://localhost:3000 in your browser"
echo ""

