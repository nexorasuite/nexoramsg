from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import quote
import time
import os
import openpyxl
from datetime import datetime
import random
import qrcode
from io import BytesIO

# Global Chrome driver (reused across calls)
driver = None

def generate_qr_code(data="https://web.whatsapp.com"):
    """Generate QR code image and save it"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    qr_path = os.path.join(os.getcwd(), 'static', 'qr_code.png')
    os.makedirs('static', exist_ok=True)
    img.save(qr_path)
    return qr_path

def get_random_delay():
    """Get random delay between 20 seconds and 3 minutes"""
    return random.uniform(20, 180)

def init_driver():
    global driver
    if driver is None:
        user_data_dir = os.path.join(os.getcwd(), 'user_data', 'default_profile')
        os.makedirs(user_data_dir, exist_ok=True)

        options = webdriver.ChromeOptions()
        options.binary_location = '/usr/bin/chromium'  # Update if needed
        options.add_argument(f'--user-data-dir={user_data_dir}')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        service = Service('/usr/bin/chromedriver')  # Update if needed
        driver = webdriver.Chrome(service=service, options=options)

        # Generate and display QR code before showing WhatsApp Web
        qr_path = generate_qr_code()
        print(f"📱 QR Code generated at: {qr_path}")
        print("🔐 Please scan the QR code from your phone to login to WhatsApp Web")
        
        # Load WhatsApp Web and wait for user login
        driver.get('https://web.whatsapp.com')
        WebDriverWait(driver, 300).until(
            EC.presence_of_element_located((By.ID, "side"))
        )
        print("✅ WhatsApp Web loaded successfully!")
    return driver

def send_whatsapp_messages_with_log(numbers, message, log_path, append=False):
    # Prepare Excel workbook for logging
    if append and os.path.exists(log_path):
        wb = openpyxl.load_workbook(log_path)
        ws = wb.active
    else:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "WhatsApp Logs"
        ws.append(['Phone Number', 'Status', 'Timestamp', 'Delay Used (sec)'])

    driver = init_driver()

    encoded_message = quote(message)

    for idx, number in enumerate(numbers):
        try:
            # Get random delay between sends
            delay = get_random_delay()
            
            url = f"https://web.whatsapp.com/send?phone={number}&text={encoded_message}"
            driver.get(url)

            # Wait for the send button and click
            send_button = WebDriverWait(driver, 40).until(
                EC.element_to_be_clickable((By.XPATH, '//span[@data-icon="send"]'))
            )
            send_button.click()

            print(f"✅ Message sent to {number}")
            ws.append([number, "Sent", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), f"{delay:.1f}"])
            
            # Random delay between messages to avoid WhatsApp ban
            print(f"⏳ Waiting {delay:.1f} seconds before next message... ({idx+1}/{len(numbers)})")
            time.sleep(delay)

        except Exception as e:
            if "Phone number shared via URL is invalid" in driver.page_source:
                print(f"⚠️ Invalid number: {number}")
                ws.append([number, "Invalid", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "-"])
            else:
                print(f"❌ Failed to send to {number}: {e}")
                ws.append([number, f"Failed: {str(e)}", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "-"])

    wb.save(log_path)
    print(f"📄 Log saved to {log_path}")

def close_driver():
    global driver
    if driver:
        driver.quit()
        driver = None


def send_telegram_messages_with_log(chat_ids, message, log_path, append=False, api_token=None):
    """
    Send messages via Telegram Bot API
    
    Args:
        chat_ids: List of Telegram chat IDs or usernames
        message: Message to send
        log_path: Path to save Excel log
        append: Whether to append to existing log
        api_token: Telegram Bot API token (from @BotFather)
    """
    import requests
    
    if not api_token:
        print("❌ Telegram API token not provided!")
        return
    
    # Prepare Excel workbook for logging
    if append and os.path.exists(log_path):
        wb = openpyxl.load_workbook(log_path)
        ws = wb.active
    else:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Telegram Logs"
        ws.append(['Chat ID', 'Status', 'Timestamp', 'Delay Used (sec)'])

    base_url = f"https://api.telegram.org/bot{api_token}/sendMessage"

    for idx, chat_id in enumerate(chat_ids):
        try:
            # Get random delay between sends
            delay = get_random_delay()
            
            payload = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            
            response = requests.post(base_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ Message sent to {chat_id}")
                ws.append([chat_id, "Sent", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), f"{delay:.1f}"])
            else:
                error_msg = response.json().get('description', 'Unknown error')
                print(f"❌ Failed to send to {chat_id}: {error_msg}")
                ws.append([chat_id, f"Failed: {error_msg}", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "-"])
            
            # Random delay between messages
            print(f"⏳ Waiting {delay:.1f} seconds before next message... ({idx+1}/{len(chat_ids)})")
            time.sleep(delay)
            
        except Exception as e:
            print(f"❌ Error sending to {chat_id}: {e}")
            ws.append([chat_id, f"Error: {str(e)}", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "-"])

    wb.save(log_path)
    print(f"📄 Log saved to {log_path}")