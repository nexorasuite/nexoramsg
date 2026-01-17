# 📱 NexoraMsg v2.0 - Quick Reference Card

## 🚀 Quick Start

### Desktop/Server (Linux/Mac/Windows)
```bash
# 1. Install
git clone https://github.com/nexorasuite/nexoramsg.git
cd nexoramsg
pip install -r requirements.txt

# 2. Run
python3 app.py

# 3. Open browser
http://localhost:5000
```

### Raspberry Pi
```bash
# Download and run setup script
curl -O https://raw.githubusercontent.com/nexorasuite/nexoramsg/main/install_raspberry_pi.sh
chmod +x install_raspberry_pi.sh
./install_raspberry_pi.sh
```

---

## 📋 Supported Platforms

### WhatsApp
```
✅ Phone numbers worldwide
✅ QR code authentication
✅ Random delays (20s-3m)
✅ Excel logging
✅ Format: 919876543210 (with country code)
```

### Telegram
```
✅ Chat IDs (numeric)
✅ Usernames (@username)
✅ Bot API integration
✅ HTML formatting
✅ Random delays
✅ Requires: TELEGRAM_BOT_TOKEN env var
```

---

## ⏱️ Timing

| Platform | Speed | Per 100 Msgs |
|----------|-------|--------------|
| WhatsApp | ~50s each | ~80 min |
| Telegram | ~2s each | ~3 min |

**Note:** WhatsApp includes 20-180s random delay per message

---

## 🔐 Authentication

### WhatsApp:
1. Start campaign → QR code generated
2. Scan with phone WhatsApp app
3. Auto-logged in
4. Ready to send

### Telegram:
1. Get token from [@BotFather](https://t.me/botfather)
2. Set: `export TELEGRAM_BOT_TOKEN="token"`
3. Start app
4. Ready to send

---

## 📊 Logging

Each campaign creates Excel file with:
- **Recipient ID** - Phone/Chat ID sent to
- **Status** - Sent/Failed/Invalid
- **Timestamp** - When sent (YYYY-MM-DD HH:MM:SS)
- **Delay Used** - Random delay applied (seconds)

---

## 🛠️ Configuration

### Chrome Location (Linux)
- Default: `/usr/bin/chromium`
- Edit: `sender.py` line 41
```python
options.binary_location = '/usr/bin/chromium'
```

### Chrome Location (Mac)
```python
options.binary_location = '/Applications/Chromium.app/Contents/MacOS/Chromium'
```

### Change Port
Edit `app.py` line 64:
```python
app.run(host='0.0.0.0', port=8000)  # Changed from 5000
```

---

## 🍓 Raspberry Pi Specific

### Installation
```bash
./install_raspberry_pi.sh
```

### Recommended Model
- **Pi 4** (4GB RAM minimum)
- **Pi 3** (works but slower)
- **Pi Zero** (not recommended)

### Auto-start Service
```bash
sudo systemctl start nexoramsg
sudo systemctl status nexoramsg
sudo systemctl stop nexoramsg
```

### Remote Access
```
http://<pi-ip>:5000
# Find Pi IP: hostname -I
```

---

## 🎯 Usage Examples

### Send WhatsApp (10 numbers)
```
1. Go to http://localhost:5000
2. Select "WhatsApp"
3. Paste 10 phone numbers (one per line)
4. Enter message
5. Click "Start Sending"
6. Scan QR code when prompted
7. Sending starts automatically
8. Download Excel log when complete
```

### Send Telegram (5 users)
```
1. Set token: export TELEGRAM_BOT_TOKEN="..."
2. Start: python3 app.py
3. Go to http://localhost:5000
4. Select "Telegram"
5. Paste 5 chat IDs or @usernames
6. Enter message (can use HTML tags)
7. Click "Start Sending"
8. Download log when complete
```

---

## ⏳ Delay Examples

Each message has random delay before next one:

| Message # | Wait Time | Cumulative |
|-----------|-----------|------------|
| 1 | - | 0:00 |
| 2 | 45 sec | 0:45 |
| 3 | 2:15 | 3:00 |
| 4 | 67 sec | 4:07 |
| 5 | 1:52 | 5:59 |

**Why?** Avoids WhatsApp bot detection and bans

---

## 🐛 Troubleshooting

### Chrome not found
```bash
# Ubuntu/Debian
sudo apt install chromium chromium-driver

# macOS
brew install chromium
```

### Port 5000 in use
```bash
sudo lsof -i :5000
kill -9 <PID>
# OR change port in app.py
```

### QR Code not generating
```bash
pip install qrcode pillow --upgrade
```

### Telegram not working
```bash
# Check token set
echo $TELEGRAM_BOT_TOKEN

# Verify bot is created
# Chat with @BotFather
```

### Slow on Raspberry Pi
1. Ensure Pi 4 with 4GB RAM
2. Close other apps
3. Increase swap file (see RASPBERRY_PI_GUIDE.md)

---

## 📁 Important Files

| File | Purpose |
|------|---------|
| `app.py` | Main Flask application |
| `sender.py` | Message sending logic |
| `templates/index.html` | Web interface |
| `user_data/` | Chrome profile cache (keep safe!) |
| `static/logs/` | Generated Excel logs |
| `requirements.txt` | Python dependencies |

---

## 🔒 Security Tips

1. ✅ Use environment variables for tokens
2. ✅ Backup `user_data/` folder regularly
3. ✅ Use HTTPS in production (nginx + SSL)
4. ✅ Restrict network access to port 5000
5. ✅ Follow platform ToS for messaging
6. ✅ Only message opted-in users

---

## 📈 Best Practices

### For WhatsApp:
- ✅ Start with small batches (5-10)
- ✅ Monitor account health
- ✅ Space out campaigns across days
- ✅ Use message variations
- ✅ Check "Invalid" in logs

### For Telegram:
- ✅ Ensure users started bot first
- ✅ Can send faster (no delays needed)
- ✅ Use HTML formatting for engagement
- ✅ Monitor rate limits (30/sec per bot)

### For Raspberry Pi:
- ✅ Set up auto-start service
- ✅ Monitor CPU/RAM usage
- ✅ Keep Chrome fresh (weekly restart)
- ✅ Enable backups
- ✅ Test before production run

---

## 📞 Support

- 📖 **Full Guide:** See README.md
- 🍓 **Pi Setup:** See RASPBERRY_PI_GUIDE.md
- 📋 **Features:** See FEATURES.md
- 🔄 **Migration:** See UPGRADE_GUIDE.md

---

## ⚡ Quick Commands

```bash
# Install
pip install -r requirements.txt

# Run
python3 app.py

# Set Telegram token
export TELEGRAM_BOT_TOKEN="your_token"

# Check if running
curl http://localhost:5000

# Stop service (Pi)
sudo systemctl stop nexoramsg

# View logs (Pi)
sudo journalctl -u nexoramsg -f

# Check Port
lsof -i :5000
```

---

**Version:** 2.0
**Updated:** January 2026
**Repository:** github.com/nexorasuite/nexoramsg

