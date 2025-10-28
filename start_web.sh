#!/bin/bash

# SmartMoneyTracker Web Interface Startup Script

echo "======================================"
echo "  SmartMoneyTracker Web Interface"
echo "======================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

# Check if required packages are installed
echo "📦 Checking dependencies..."
python3 -c "import flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Flask is not installed. Installing dependencies..."
    pip3 install -r requirements.txt
fi

echo ""
echo "🚀 Starting SmartMoneyTracker Web Server..."
echo ""
echo "📍 Server will be available at: http://localhost:8001"
echo "📍 Press Ctrl+C to stop the server"
echo ""
echo "======================================"
echo ""

# Start the Flask application
python3 app.py
