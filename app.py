from flask import Flask, render_template, request, redirect, url_for
from sender import send_whatsapp_messages_with_log, send_telegram_messages_with_log, close_driver
from urllib.parse import quote
import uuid
import os
import threading
import time

app = Flask(__name__)

sending_thread = None
stop_flag = False

# Telegram API token - should be set via environment variable or config
TELEGRAM_API_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')

def clean_number(num):
    return ''.join(filter(str.isdigit, num))

def background_send(platform, recipients, message, log_path):
    global stop_flag
    stop_flag = False
    
    if platform == 'whatsapp':
        send_whatsapp_messages_with_log(recipients, message, log_path, append=True)
    elif platform == 'telegram':
        send_telegram_messages_with_log(recipients, message, log_path, append=True, api_token=TELEGRAM_API_TOKEN)
    
    close_driver()

@app.route('/', methods=['GET', 'POST'])
def index():
    global sending_thread

    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'Stop':
            global stop_flag
            stop_flag = True
            return render_template('index.html', uploaded=True, status='⛔ Stopped', telegram_token=bool(TELEGRAM_API_TOKEN))

        platform = request.form.get('platform', 'whatsapp')
        recipients_raw = request.form.get('recipients', '')
        message = request.form.get('message', '')

        if not recipients_raw.strip() or not message.strip():
            return render_template('index.html', uploaded=False, error="❌ Please enter recipients and message.", telegram_token=bool(TELEGRAM_API_TOKEN))

        # Clean recipients based on platform
        if platform == 'whatsapp':
            recipients = [clean_number(num.strip()) for num in recipients_raw.split('\n') if num.strip()]
        else:  # telegram
            recipients = [r.strip() for r in recipients_raw.split('\n') if r.strip()]

        log_filename = f'{platform}_log_{uuid.uuid4().hex[:6]}.xlsx'
        log_path = os.path.join('static', 'logs', log_filename)
        os.makedirs('static/logs', exist_ok=True)

        if sending_thread and sending_thread.is_alive():
            return render_template('index.html', uploaded=False, error="⚠️ Sending already in progress...", telegram_token=bool(TELEGRAM_API_TOKEN))

        sending_thread = threading.Thread(target=background_send, args=(platform, recipients, message, log_path))
        sending_thread.start()

        return render_template('index.html', uploaded=True, count=len(recipients), log_file=log_filename, status="✅ Sending started...", platform=platform, telegram_token=bool(TELEGRAM_API_TOKEN))

    return render_template('index.html', uploaded=False, telegram_token=bool(TELEGRAM_API_TOKEN))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
