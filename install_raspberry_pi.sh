#!/bin/bash

# NexoraMsg Raspberry Pi Installation Script
# This script automates the setup on Raspberry Pi OS

set -e

echo "🚀 NexoraMsg - Raspberry Pi Installation"
echo "========================================"
echo ""

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo "⚠️  Warning: This doesn't appear to be a Raspberry Pi"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Step 1: Update system
echo "📦 Step 1: Updating system packages..."
sudo apt update
sudo apt upgrade -y

# Step 2: Install dependencies
echo "📦 Step 2: Installing Chromium and dependencies..."
sudo apt install -y python3 python3-pip python3-dev
sudo apt install -y chromium chromium-driver
sudo apt install -y git wget curl

# Step 3: Clone or navigate to project
echo "📦 Step 3: Setting up NexoraMsg..."
if [ ! -d "nexoramsg" ]; then
    echo "Cloning repository..."
    git clone https://github.com/nexorasuite/nexoramsg.git
else
    echo "Repository already exists, updating..."
    cd nexoramsg
    git pull
    cd ..
fi

cd nexoramsg

# Step 4: Install Python dependencies
echo "📦 Step 4: Installing Python packages..."
pip3 install -r requirements.txt

# Step 5: Create necessary directories
echo "📁 Step 5: Creating directories..."
mkdir -p static/logs
mkdir -p user_data/default_profile

# Step 6: Ask about Telegram setup
echo ""
echo "🤖 Telegram Setup (Optional)"
read -p "Do you want to set up Telegram bot? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Get your bot token from @BotFather on Telegram"
    read -p "Enter your Telegram Bot Token: " TELEGRAM_TOKEN
    
    echo "export TELEGRAM_BOT_TOKEN='$TELEGRAM_TOKEN'" >> ~/.bashrc
    export TELEGRAM_BOT_TOKEN="$TELEGRAM_TOKEN"
    echo "✅ Telegram token set!"
fi

# Step 7: Ask about SystemD service
echo ""
echo "🔄 SystemD Service Setup (Auto-start on boot)"
read -p "Set up as SystemD service? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    PROJECT_PATH=$(pwd)
    
    echo "Creating SystemD service file..."
    sudo tee /etc/systemd/system/nexoramsg.service > /dev/null <<EOF
[Unit]
Description=NexoraMsg Bulk Messaging Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_PATH
ExecStart=/usr/bin/python3 $PROJECT_PATH/app.py
Restart=always
RestartSec=10
Environment="TELEGRAM_BOT_TOKEN=$TELEGRAM_TOKEN"

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable nexoramsg
    
    echo "✅ Service created! Start with: sudo systemctl start nexoramsg"
fi

# Step 8: Test installation
echo ""
echo "✅ Installation Complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Start the app:"
echo "   python3 app.py"
echo ""
echo "2. Open your browser:"
echo "   http://localhost:5000"
echo ""
echo "3. For remote access (from another device):"
HOSTNAME=$(hostname -I | awk '{print $1}')
echo "   http://$HOSTNAME:5000"
echo ""
echo "📖 For detailed setup guide, see: RASPBERRY_PI_GUIDE.md"
echo ""

# Optional: Start the app now
read -p "Start NexoraMsg now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 Starting NexoraMsg..."
    python3 app.py
fi
