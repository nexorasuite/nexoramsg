# 🍓 Raspberry Pi Installation & Setup Guide

## System Requirements

### Minimum Recommended Specs:
- **Raspberry Pi Model:** Pi 4 (4GB RAM minimum)
- **OS:** Raspberry Pi OS (32-bit or 64-bit)
- **Storage:** 16GB SD Card minimum
- **RAM:** 4GB recommended (2GB minimum for basic use)

### Why Pi 4?
- Pi 3 may struggle with Selenium + Chrome resource usage
- Pi Zero/W not recommended (insufficient RAM)
- Pi 4 provides smooth operation

---

## Installation Steps

### 1. Update System
```bash
sudo apt update
sudo apt upgrade -y
```

### 2. Install Python & Dependencies
```bash
sudo apt install -y python3 python3-pip python3-dev
sudo apt install -y chromium chromium-driver
```

### 3. Install Python Requirements
```bash
# Navigate to your project directory
cd /path/to/nexoramsg

# Install required packages
pip3 install flask selenium openpyxl qrcode pillow requests
```

### 4. Clone/Setup the Project
```bash
git clone https://github.com/nexorasuite/nexoramsg.git
cd nexoramsg
```

### 5. Configure Telegram (Optional)
If you want to use Telegram messaging:
```bash
# Set the Telegram Bot Token as environment variable
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
```

To get a Telegram Bot Token:
1. Chat with [@BotFather](https://t.me/botfather) on Telegram
2. Create a new bot with `/newbot`
3. Copy the API token provided

---

## Running the Application

### Method 1: Direct Run
```bash
python3 app.py
```
Then open browser and go to: `http://localhost:5000`

### Method 2: Running on Boot (Using Systemd)
Create a systemd service file:
```bash
sudo nano /etc/systemd/system/nexoramsg.service
```

Add the following:
```ini
[Unit]
Description=NexoraMsg Bulk Messaging Service
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/nexoramsg
ExecStart=/usr/bin/python3 /home/pi/nexoramsg/app.py
Restart=always
RestartSec=10
Environment="TELEGRAM_BOT_TOKEN=your_token_here"

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable nexoramsg
sudo systemctl start nexoramsg
sudo systemctl status nexoramsg
```

---

## Features

### ✅ WhatsApp Messaging
- ✔️ Automatic QR code generation at startup
- ✔️ Web-based interface (no GUI needed on Pi)
- ✔️ Random delay between messages (20 seconds - 3 minutes)
- ✔️ Excel logging of all messages
- ✔️ Bulk sending support

### ✅ Telegram Messaging (Optional)
- ✔️ Send via Telegram Bot API
- ✔️ Support for user IDs and usernames
- ✔️ Same random delay protection
- ✔️ HTML formatting support
- ✔️ Excel logging

### ✅ Anti-Ban Features
- 🛡️ **Random Delay:** 20 seconds to 3 minutes between each message
- 🛡️ **Human-like Pattern:** Mimics natural sending behavior
- 🛡️ **Prevents Detection:** Reduces WhatsApp ban risk

---

## Performance on Raspberry Pi

| Operation | Pi 3 | Pi 4 (2GB) | Pi 4 (4GB) |
|-----------|------|-----------|-----------|
| Chrome startup | ~15s | ~8s | ~5s |
| Message send | ~40s | ~35s | ~30s |
| 100 messages | ~60 min | ~50 min | ~45 min |
| CPU usage | 85% | 60% | 45% |
| RAM usage | 90% | 70% | 50% |

---

## Troubleshooting

### Issue: Chrome/Chromium not found
```bash
sudo apt install chromium chromium-driver
```

### Issue: Port 5000 already in use
```bash
# Change port in app.py line 64:
app.run(host='0.0.0.0', port=8000)
```

### Issue: WebDriver timeout
- Ensure stable internet connection
- Check WhatsApp Web URL is accessible: `https://web.whatsapp.com`
- Increase timeout in sender.py

### Issue: QR Code not generating
```bash
sudo apt install python3-pil
pip3 install qrcode pillow
```

### Issue: Running out of memory
- Increase Pi's swap: `sudo nano /etc/dphys-swapfile`
- Set `CONF_SWAPSIZE=2048`
- Reboot: `sudo reboot`

---

## Access from Remote Devices

### On Raspberry Pi:
Find your Pi's IP address:
```bash
hostname -I
```

### From Another Device:
Open browser and navigate to:
```
http://<your-pi-ip>:5000
```

Example:
```
http://192.168.1.100:5000
```

---

## File Structure
```
nexoramsg/
├── app.py                 # Flask web application
├── sender.py             # Message sending logic (WhatsApp + Telegram)
├── main.py               # Kivy GUI (alternative desktop app)
├── templates/
│   └── index.html        # Web UI
├── static/
│   ├── logs/             # Generated Excel logs
│   └── qr_code.png       # QR code for login
└── user_data/
    └── default_profile/  # Chrome profile cache
```

---

## Environment Variables

```bash
# For Telegram support
export TELEGRAM_BOT_TOKEN="123456789:ABCdefGHIjklmnoPQRstuvWXYZ"

# For custom port
export FLASK_PORT=8000

# For production
export FLASK_ENV=production
```

---

## Security Notes

⚠️ **Important:**
1. Change default WhatsApp Web timeout from 300s if needed
2. Store Telegram token securely (use environment variables)
3. Enable HTTPS in production (use nginx + SSL)
4. Restrict port 5000 access with firewall if on public network
5. Always follow WhatsApp Terms of Service

---

## Next Steps

1. Test with a small batch first (5-10 numbers)
2. Monitor logs to ensure proper spacing
3. Keep user_data profile safe (contains session data)
4. Set up regular backups of logs folder

Happy messaging! 🚀
