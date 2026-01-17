# NexoraMsg - Bulk Messaging Platform

Send WhatsApp and Telegram messages at scale with **human-like delays** to avoid bans.

![Version](https://img.shields.io/badge/version-2.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

---

## 🎯 Features

### WhatsApp Messaging
- ✅ **Automated QR Code Login** - Secure authentication via QR code
- ✅ **Bulk Sending** - Send to thousands of numbers
- ✅ **Anti-Ban Protection** - Random 20s-3m delays between sends
- ✅ **Excel Logging** - Track all messages sent
- ✅ **Web-based Interface** - No GUI needed, works on headless systems

### Telegram Messaging  
- ✅ **Bot API Integration** - Send via Telegram bots
- ✅ **User & Group Support** - Send to users and channels
- ✅ **HTML Formatting** - Rich message formatting
- ✅ **Same Anti-Ban Logic** - Random delays applied

### Raspberry Pi Ready
- ✅ **Lightweight** - Runs on Pi 4+ 
- ✅ **Web Interface** - Access from any device on network
- ✅ **SystemD Integration** - Auto-start on boot
- ✅ **Resource Optimized** - Efficient CPU/RAM usage

---

## 📋 Requirements

### For Desktop/Server:
- Python 3.8+
- Chromium/Chrome browser
- ChromeDriver
- 2GB RAM minimum (4GB recommended)

### For Raspberry Pi:
- Raspberry Pi 4 (4GB RAM recommended)
- Raspberry Pi OS
- See [Raspberry Pi Setup Guide](RASPBERRY_PI_GUIDE.md)

---

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/nexorasuite/nexoramsg.git
cd nexoramsg
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Application
```bash
python3 app.py
```

### 4. Access Web Interface
Open browser: `http://localhost:5000`

---

## 🔧 Configuration

### WhatsApp Setup
1. Start the application
2. QR code will display when you start first campaign
3. Scan with your WhatsApp phone
4. Authenticate and start sending

### Telegram Setup (Optional)
```bash
# Get token from @BotFather on Telegram
export TELEGRAM_BOT_TOKEN="123456789:ABCdefGHIjklmnoPQRstuvWXYZ"
python3 app.py
```

---

## 📊 Anti-Ban Protection

All messages include **random delays**:
- **Minimum:** 20 seconds
- **Maximum:** 3 minutes
- **Applied:** Between each message
- **Prevents:** WhatsApp rate limiting and bans

This mimics human-like sending behavior to avoid platform restrictions.

---

## 📁 Project Structure

```
nexoramsg/
├── app.py                      # Flask web application
├── sender.py                   # Message sending engine
├── main.py                     # Kivy GUI alternative
├── requirements.txt            # Python dependencies
├── templates/
│   └── index.html             # Web interface
├── static/
│   ├── logs/                  # Excel message logs
│   └── qr_code.png           # QR code image
├── user_data/
│   └── default_profile/       # Chrome session cache
├── RASPBERRY_PI_GUIDE.md      # Detailed Pi setup
└── README.md                  # This file
```

---

## 📈 Usage Examples

### WhatsApp - Via Web UI
1. Select **WhatsApp** tab
2. Paste phone numbers (with country code)
3. Enter message
4. Click **Start Sending**
5. Scan QR code when prompted
6. Download Excel log when complete

### Telegram - Via Web UI
1. Select **Telegram** tab
2. Paste user IDs or @usernames
3. Enter message (supports HTML tags)
4. Click **Start Sending**
5. Download log when complete

### Python API
```python
from sender import send_whatsapp_messages_with_log, send_telegram_messages_with_log

# WhatsApp
send_whatsapp_messages_with_log(
    numbers=['919876543210', '918765432109'],
    message='Hello!',
    log_path='logs/whatsapp_log.xlsx'
)

# Telegram
send_telegram_messages_with_log(
    chat_ids=['123456789', '@username'],
    message='Hello from Bot!',
    log_path='logs/telegram_log.xlsx',
    api_token='YOUR_BOT_TOKEN'
)
```

---

## 🔐 Security & Best Practices

⚠️ **Important:**

1. **WhatsApp Terms of Service** - Use responsibly, only send to opted-in users
2. **Rate Limits** - Random delays help but respect platform limits
3. **Token Security** - Use environment variables for Telegram tokens
4. **Backup** - Keep logs and user_data folder backed up
5. **HTTPS** - Use reverse proxy (nginx) with SSL in production

---

## 🛠️ Advanced Configuration

### Custom Delay Range
Edit `sender.py`:
```python
def get_random_delay():
    return random.uniform(30, 120)  # 30-120 seconds
```

### Chrome Options
Edit `sender.py` in `init_driver()`:
```python
options.add_argument('--headless')  # Headless mode
options.add_argument('--disable-gpu')  # Disable GPU
```

### Change Port
Edit `app.py`:
```python
app.run(host='0.0.0.0', port=8000)  # Port 8000 instead
```

---

## 📝 Logging & Monitoring

Each campaign generates an Excel file with:
- **Phone Number / Chat ID** - Recipient identifier
- **Status** - Sent/Failed/Invalid
- **Timestamp** - When message was sent  
- **Delay Used** - Random delay applied

Access logs in `static/logs/` folder or download from web interface.

---

## 🤝 Support for Raspberry Pi

For detailed Raspberry Pi setup including:
- SystemD service configuration
- Memory optimization
- Remote access setup
- Troubleshooting

See: [RASPBERRY_PI_GUIDE.md](RASPBERRY_PI_GUIDE.md)

---

## 🐛 Troubleshooting

### Chrome/Chromium not found
```bash
# Ubuntu/Debian
sudo apt install chromium chromium-driver

# macOS
brew install chromium
```

### Port already in use
```bash
lsof -i :5000  # Find what's using port 5000
kill -9 <PID>
```

### WebDriver timeout
- Check internet connection
- Verify `web.whatsapp.com` is accessible
- Increase timeout in `sender.py`: `WebDriverWait(driver, 60)`

### QR Code not displaying
```bash
pip install qrcode pillow --upgrade
```

---

## 📄 License

MIT License - See LICENSE file

---

## 📞 Support

- 🎓 [Raspberry Pi Guide](RASPBERRY_PI_GUIDE.md)
- 🐛 Report issues on GitHub
- 💬 Questions? Check existing issues first

---

## ⚠️ Disclaimer

This tool should only be used for:
- ✅ Marketing to opted-in customers
- ✅ Account notifications
- ✅ Service updates
- ✅ Personal group messaging

❌ **NOT** for:
- Spam or unsolicited messages
- Phishing or scams
- Violating platform Terms of Service

Users are responsible for complying with all applicable laws and platform policies.

---

**Built with ❤️ by NexoraSuite**

