#!/bin/bash

# NexoraMsg - Raspberry Pi Diagnostic Script
# Helps identify and fix issues

echo "🍓 NexoraMsg - Raspberry Pi Diagnostics"
echo "======================================"
echo ""

# Check if on Raspberry Pi
echo "📋 System Information:"
if grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo "✅ Running on Raspberry Pi"
    cat /proc/cpuinfo | grep "Model" | head -1
else
    echo "⚠️  Not running on Raspberry Pi (or info not available)"
fi
echo ""

# Check Python
echo "🐍 Python Setup:"
python3 --version
if [ -d "venv" ]; then
    echo "✅ Virtual environment exists"
    source venv/bin/activate 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "✅ Virtual environment activated"
    fi
else
    echo "❌ Virtual environment NOT found"
    echo "   Fix: python3 -m venv venv && source venv/bin/activate"
fi
echo ""

# Check Python packages
echo "📦 Required Python Packages:"
python3 -c "import selenium; print('✅ Selenium')" 2>/dev/null || echo "❌ Selenium - Run: pip install selenium"
python3 -c "import flask; print('✅ Flask')" 2>/dev/null || echo "❌ Flask - Run: pip install flask"
python3 -c "import openpyxl; print('✅ openpyxl')" 2>/dev/null || echo "❌ openpyxl - Run: pip install openpyxl"
python3 -c "import qrcode; print('✅ qrcode')" 2>/dev/null || echo "❌ qrcode - Run: pip install qrcode"
echo ""

# Check Chromium
echo "🌐 Chromium Browser:"
if command -v chromium-browser &> /dev/null; then
    echo "✅ Found: chromium-browser at $(which chromium-browser)"
    chromium-browser --version
elif command -v chromium &> /dev/null; then
    echo "✅ Found: chromium at $(which chromium)"
    chromium --version
elif command -v google-chrome &> /dev/null; then
    echo "✅ Found: google-chrome at $(which google-chrome)"
    google-chrome --version
else
    echo "❌ Chromium not found!"
    echo "   Fix: sudo apt install -y chromium-browser"
fi
echo ""

# Check ChromeDriver
echo "🔧 ChromeDriver:"
if command -v chromedriver &> /dev/null; then
    echo "✅ Found: $(which chromedriver)"
    chromedriver --version
else
    echo "⚠️  ChromeDriver not found (might be bundled with Chromium)"
    if [ -f "/usr/lib/chromium-browser/chromedriver" ]; then
        echo "✅ Found at: /usr/lib/chromium-browser/chromedriver"
    fi
fi
echo ""

# Check resources
echo "💾 System Resources:"
echo "RAM:"
free -h | grep "Mem:" | awk '{print "  Total: " $2 ", Used: " $3 ", Free: " $4}'

echo "Disk:"
df -h / | tail -1 | awk '{print "  Total: " $2 ", Used: " $3 ", Free: " $4}'

echo "Temperature:"
if command -v vcgencmd &> /dev/null; then
    vcgencmd measure_temp 2>/dev/null || echo "  ⚠️  Could not read temperature"
fi
echo ""

# Check connectivity
echo "🌐 Network Connectivity:"
if ping -c 1 web.whatsapp.com &> /dev/null; then
    echo "✅ Can reach web.whatsapp.com"
else
    echo "❌ Cannot reach web.whatsapp.com"
fi

if ping -c 1 api.telegram.org &> /dev/null; then
    echo "✅ Can reach api.telegram.org (Telegram)"
else
    echo "❌ Cannot reach api.telegram.org"
fi
echo ""

# Check project files
echo "📁 Project Files:"
if [ -f "app.py" ]; then
    echo "✅ app.py found"
else
    echo "❌ app.py NOT found"
fi

if [ -f "sender.py" ]; then
    echo "✅ sender.py found"
else
    echo "❌ sender.py NOT found"
fi

if [ -f "requirements.txt" ]; then
    echo "✅ requirements.txt found"
else
    echo "❌ requirements.txt NOT found"
fi

if [ -d "templates" ]; then
    echo "✅ templates/ directory found"
else
    echo "❌ templates/ directory NOT found"
fi

if [ -d "static" ]; then
    echo "✅ static/ directory found"
else
    echo "❌ static/ directory NOT found (will be created on first run)"
fi
echo ""

# Summary
echo "======================================"
echo "📊 Summary:"
echo ""
if python3 -c "import selenium, flask, openpyxl" 2>/dev/null; then
    echo "✅ Python packages OK"
else
    echo "❌ Missing Python packages - run: pip install -r requirements.txt"
fi

if command -v chromium-browser &> /dev/null || command -v chromium &> /dev/null; then
    echo "✅ Chromium OK"
else
    echo "❌ Chromium NOT installed - run: sudo apt install -y chromium-browser"
fi

if [ -f "app.py" ] && [ -f "sender.py" ]; then
    echo "✅ Project files OK"
else
    echo "❌ Project files missing"
fi

echo ""
echo "Ready to run: python3 app.py"
echo ""
