# 🍓 Raspberry Pi - Debugging & Fix Guide

## ⚠️ Issues You Encountered

### Issue 1: Selenium Module Not Found
```
ModuleNotFoundError: No module named 'selenium'
```

**Solution:**
```bash
# Must use virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Issue 2: Chromium Crashes (Stacktrace)
```
❌ Failed to send to 919825728291: Message: Stacktrace: #0 0x005585decb68...
```

**Root Cause:** Chromium rendering issues on Raspberry Pi (GPU/memory related)

**Solutions Applied:**
1. ✅ Disable GPU rendering: `--disable-gpu`
2. ✅ Disable 3D APIs: `--disable-3d-apis`
3. ✅ Disable extensions: `--disable-extensions`
4. ✅ Added error handling for chromedriver path

---

## 🔧 Installation Steps for Raspberry Pi (Corrected)

### Step 1: Update System
```bash
sudo apt update
sudo apt upgrade -y
```

### Step 2: Install Dependencies
```bash
# Install Chromium (full browser, not just chromedriver)
sudo apt install -y chromium-browser chromium-codecs-ffmpeg

# Install Python and required tools
sudo apt install -y python3 python3-pip python3-venv git

# Install additional libraries for Pi
sudo apt install -y libatlas-base-dev libjasper-dev libtiff5 libjasper1 libharfp-arm
sudo apt install -y libwebp6 libtiff5 libjasper1 libharfp-arm
```

### Step 3: Create Project Directory
```bash
cd ~
git clone https://github.com/nexorasuite/nexoramsg.git
cd nexoramsg
```

### Step 4: Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 5: Install Python Packages
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 6: Set Correct Chromium Path (IMPORTANT!)
On Raspberry Pi, Chromium location is typically `/usr/bin/chromium-browser`, NOT `/usr/bin/chromium`

Edit `sender.py` line ~44:
```python
options.binary_location = '/usr/bin/chromium-browser'  # For Raspberry Pi
# OR try:
options.binary_location = '/snap/bin/chromium'  # If installed via snap
```

To find Chromium:
```bash
which chromium-browser
which chromium
which chromium-browser
ls -la /usr/bin/chromium*
```

---

## 🚀 Running on Raspberry Pi (Correct Method)

### Method 1: Direct Run (Testing)
```bash
# Always activate venv first!
source venv/bin/activate

# Run the app
python3 app.py

# You should see:
# * Running on all addresses (0.0.0.0)
# * Running on http://192.168.31.109:5000
```

### Method 2: Access from Your Computer
1. Find your Pi's IP:
   ```bash
   hostname -I
   ```
2. From your computer browser:
   ```
   http://<pi-ip>:5000
   ```
   Example: `http://192.168.31.109:5000`

### Method 3: Set Up Auto-Start (SystemD)
```bash
# Create service file
sudo nano /etc/systemd/system/nexoramsg.service
```

Paste:
```ini
[Unit]
Description=NexoraMsg Messaging Service
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/nexoramsg
ExecStart=/home/pi/nexoramsg/venv/bin/python /home/pi/nexoramsg/app.py
Restart=always
RestartSec=10
Environment="TELEGRAM_BOT_TOKEN=your_token_here"

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable nexoramsg
sudo systemctl start nexoramsg

# Check status
sudo systemctl status nexoramsg
```

---

## ✅ What's Working Now

Your **first run was SUCCESSFUL!** ✅

```
✅ WhatsApp Web ready
📨 Sending to 919099028291
✅ Sent to 919099028291
⏳ Waiting 54.4s (1/2)
📨 Sending to 9825728291
✅ Sent to 9825728291
⏳ Waiting 109.5s (2/2)
📄 Log saved to static/logs/whatsapp_log_bca5ca.xlsx
```

**What this means:**
- ✅ Messages ARE being sent
- ✅ Random delays working (54.4s, 109.5s)
- ✅ Logging working
- ✅ Only issue: UI wasn't updating (FIXED)

---

## 🎯 Real-Time Dashboard Features

Your app now has a **live dashboard** that shows:

1. **Progress Bar** - Visual percentage complete
2. **Live Stats** - Sent/Failed/Invalid count updating in real-time
3. **Current Status** - Which number is being sent
4. **Current Delay** - How long waiting before next message
5. **Time Estimates** - How long remaining
6. **Auto-refresh** - Updates every 1 second

### Accessing the Dashboard
1. Open: `http://192.168.31.109:5000` (your Pi IP)
2. Enter numbers and message
3. Click "Start Sending"
4. Automatically redirected to **live dashboard**
5. Watch real-time progress!

---

## 📊 Timing Configuration

Already set in `sender.py`:
```python
def get_random_delay():
    """Get random delay between 35 seconds and 3 minutes"""
    return random.uniform(35, 180)
```

This means:
- **Minimum delay:** 35 seconds
- **Maximum delay:** 180 seconds (3 minutes)
- **Random:** Different each time
- **Logged:** Saved in Excel

---

## 🔧 Common Pi Issues & Fixes

### Issue: Still getting Chromium crash after update?

**Fix 1: Increase Swap Space**
```bash
# Edit swap config
sudo nano /etc/dphys-swapfile

# Change line to:
CONF_SWAPSIZE=2048

# Restart swap
sudo /etc/init.d/dphys-swapfile restart
```

**Fix 2: Use Different Chromium Options**
Edit `sender.py` around line 40-60:
```python
options.add_argument('--disable-dev-shm-usage')  # Keep this
options.add_argument('--disable-gpu')            # Keep this
options.add_argument('--disable-software-rasterizer')
options.add_argument('--disable-3d-apis')

# Try removing if still crashes:
# options.add_argument('--single-process')  # Don't use on Pi
```

**Fix 3: Use Brave Browser Instead of Chromium**
```bash
sudo apt install -y brave-browser

# Edit sender.py line 44:
options.binary_location = '/usr/bin/brave-browser'
```

### Issue: Messages send but very slow?

Pi 4 is normal speed. If too slow:
```bash
# Check CPU/RAM usage
htop

# Kill other processes using RAM
# Typical: Firefox, Spotify, etc.
```

### Issue: "Cannot find chromedriver"?

Chromium on Pi doesn't need separate chromedriver. Edit `sender.py`:
```python
try:
    service = Service('/usr/bin/chromedriver')
    driver = webdriver.Chrome(service=service, options=options)
except:
    # Fallback - use system PATH
    driver = webdriver.Chrome(options=options)
```

---

## 📋 Step-by-Step Fix (Start Fresh)

If still having issues, follow this:

```bash
# 1. Stop current process
^C

# 2. Deactivate venv
deactivate

# 3. Remove old venv
rm -rf venv

# 4. Create new venv
python3 -m venv venv
source venv/bin/activate

# 5. Install fresh
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# 6. Fix Chromium path
nano sender.py
# Change line 44 to: options.binary_location = '/usr/bin/chromium-browser'

# 7. Run
python3 app.py
```

---

## 🎯 Expected Output (Correct Behavior)

When you run `python3 app.py` on Pi:

```
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.31.109:5000
Press CTRL+C to quit

[Then when you send messages from web UI:]

📱 QR Code generated at: /home/pi/nexoramsg/static/qr_code.png
🔐 Please scan the QR code from your phone to login to WhatsApp Web
✅ WhatsApp Web loaded successfully!
📨 Sending to 919099028291
⏳ Waiting 45.2s (1/10)
✅ Sent to 919099028291
📨 Sending to 9825728291
⏳ Waiting 127.8s (2/10)
✅ Sent to 9825728291
📄 Log saved to static/logs/whatsapp_log_abc123.xlsx
```

If you see `✅ Sent` messages, **it's working!** The dashboard shows live progress.

---

## 📞 Quick Diagnostics

### Check if Chromium installed:
```bash
which chromium-browser
chromium-browser --version
```

### Check if Python packages installed:
```bash
source venv/bin/activate
python3 -c "import selenium; print('✅ Selenium OK')"
python3 -c "import flask; print('✅ Flask OK')"
```

### Check Pi resources:
```bash
free -h        # RAM usage
df -h          # Disk usage
vcgencmd measure_temp  # Temperature
```

### Test WhatsApp Web connection:
```bash
curl https://web.whatsapp.com
```

---

## ✨ New Features Added

1. **Real-Time Dashboard** ✅
   - Live progress bar
   - Auto-updating stats
   - Current message display
   - Current delay display

2. **Task Queue** ✅
   - Multiple tasks tracked
   - Task status API
   - Task history

3. **Better Pi Support** ✅
   - GPU rendering disabled
   - Memory optimizations
   - Better error handling
   - Fallback for chromedriver

4. **Timing Control** ✅
   - 35-180 seconds random delay
   - Fully configurable
   - Logged for transparency

---

## 🚀 Next Steps

1. **Test Run:**
   ```bash
   source venv/bin/activate
   python3 app.py
   ```

2. **Open Dashboard:**
   ```
   http://192.168.31.109:5000
   ```

3. **Send Test Messages:**
   - Enter 2-3 test numbers
   - Watch live dashboard
   - Check Excel log after

4. **Scale Up:**
   - When working, try larger batches
   - Monitor CPU/RAM
   - Adjust if needed

---

**Your app IS working! Dashboard now shows real-time updates.** 🎉

Need help? Check the output - if you see `✅ Sent` messages, messaging is working!

