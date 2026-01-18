#!/bin/bash

# NexoraMsg Real-Time Dashboard - Test Script
# Run this to test the new dashboard on Raspberry Pi

echo "🚀 NexoraMsg Real-Time Dashboard Test"
echo "======================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found!"
    exit 1
fi

echo "✅ Python 3 found"

# Check if Flask is installed
if ! python3 -c "import flask" 2>/dev/null; then
    echo "📦 Installing Flask..."
    pip3 install flask
fi

echo "✅ Flask installed"

# Check if Selenium is installed
if ! python3 -c "import selenium" 2>/dev/null; then
    echo "📦 Installing Selenium..."
    pip3 install selenium
fi

echo "✅ Selenium installed"

# Start the app
echo ""
echo "🎯 Starting NexoraMsg app..."
echo ""
echo "📝 Access the app at:"
echo "   Local:  http://localhost:5000"
echo "   Remote: http://$(hostname -I | awk '{print $1}'):5000"
echo ""
echo "✅ Real-time dashboard will load after you send messages"
echo ""
echo "Press CTRL+C to stop the server"
echo ""

# Run the app
cd /workspaces/nexoramsg 2>/dev/null || cd ~/nexoramsg 2>/dev/null || cd .
python3 app.py
