from flask import Flask, render_template, request, redirect, url_for, jsonify
from sender import send_whatsapp_messages_with_log, send_telegram_messages_with_log, close_driver
from urllib.parse import quote
import uuid
import os
import threading
import time
from queue import Queue
from datetime import datetime
import json

app = Flask(__name__)

# Task state tracking for real-time dashboard
current_task = {
    'id': None,
    'platform': None,
    'status': 'idle',  # idle, running, paused, completed, failed
    'progress': 0,
    'total': 0,
    'current': 0,
    'message': '',
    'messages': [],
    'start_time': None,
    'elapsed': 0,
    'estimated_remaining': 0,
    'log_file': None,
}

sending_thread = None
stop_flag = False
pause_flag = False

# Telegram API token
TELEGRAM_API_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')

def clean_number(num):
    return ''.join(filter(str.isdigit, num))

def background_send(platform, recipients, message, log_path):
    """Background task for sending messages with real-time progress"""
    global stop_flag, pause_flag, current_task
    
    stop_flag = False
    pause_flag = False
    
    current_task['status'] = 'running'
    current_task['start_time'] = datetime.now()
    current_task['total'] = len(recipients)
    current_task['messages'] = []
    
    if platform == 'whatsapp':
        send_whatsapp_messages_with_log(recipients, message, log_path, append=True)
    elif platform == 'telegram':
        send_telegram_messages_with_log(recipients, message, log_path, append=True, api_token=TELEGRAM_API_TOKEN)
    
    close_driver()
    current_task['status'] = 'completed'

@app.route('/', methods=['GET', 'POST'])
def index():
    global sending_thread, stop_flag, current_task

    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'Stop':
            stop_flag = True
            current_task['status'] = 'stopped'
            return render_template('dashboard.html', 
                                 task=current_task,
                                 telegram_token=bool(TELEGRAM_API_TOKEN),
                                 status='⛔ Stopped')

        platform = request.form.get('platform', 'whatsapp')
        recipients_raw = request.form.get('recipients', '')
        message = request.form.get('message', '')

        if not recipients_raw.strip() or not message.strip():
            return render_template('dashboard.html', 
                                 uploaded=False, 
                                 error="❌ Please enter recipients and message.",
                                 task=current_task,
                                 telegram_token=bool(TELEGRAM_API_TOKEN))

        # Clean recipients
        if platform == 'whatsapp':
            recipients = [clean_number(num.strip()) for num in recipients_raw.split('\n') if num.strip()]
        else:
            recipients = [r.strip() for r in recipients_raw.split('\n') if r.strip()]

        log_filename = f'{platform}_log_{uuid.uuid4().hex[:6]}.xlsx'
        log_path = os.path.join('static', 'logs', log_filename)
        os.makedirs('static/logs', exist_ok=True)

        # Setup task
        current_task['id'] = uuid.uuid4().hex[:8]
        current_task['platform'] = platform
        current_task['total'] = len(recipients)
        current_task['current'] = 0
        current_task['progress'] = 0
        current_task['status'] = 'running'
        current_task['message'] = message
        current_task['messages'] = []
        current_task['log_file'] = log_filename
        current_task['start_time'] = datetime.now()

        # Start background thread
        sending_thread = threading.Thread(target=background_send, args=(platform, recipients, message, log_path))
        sending_thread.daemon = True
        sending_thread.start()

        return render_template('dashboard.html', 
                             uploaded=True, 
                             count=len(recipients), 
                             log_file=log_filename,
                             task=current_task,
                             platform=platform,
                             telegram_token=bool(TELEGRAM_API_TOKEN),
                             status="✅ Sending started...")

    return render_template('dashboard.html', 
                         uploaded=False,
                         task=current_task,
                         telegram_token=bool(TELEGRAM_API_TOKEN))

@app.route('/api/progress', methods=['GET'])
def get_progress():
    """API endpoint for real-time progress updates"""
    global current_task
    
    if current_task['start_time']:
        elapsed = (datetime.now() - current_task['start_time']).total_seconds()
        current_task['elapsed'] = int(elapsed)
        
        if current_task['current'] > 0 and current_task['current'] < current_task['total']:
            avg_time = elapsed / current_task['current']
            remaining = (current_task['total'] - current_task['current']) * avg_time
            current_task['estimated_remaining'] = int(remaining)
        
        if current_task['total'] > 0:
            current_task['progress'] = int((current_task['current'] / current_task['total'] * 100))
    
    return jsonify(current_task)

@app.route('/api/pause', methods=['POST'])
def pause_task():
    """Pause current task"""
    global pause_flag
    pause_flag = True
    current_task['status'] = 'paused'
    return jsonify({'status': 'paused'})

@app.route('/api/resume', methods=['POST'])
def resume_task():
    """Resume paused task"""
    global pause_flag
    pause_flag = False
    current_task['status'] = 'running'
    return jsonify({'status': 'running'})

@app.route('/api/stop', methods=['POST'])
def stop_task():
    """Stop current task"""
    global stop_flag
    stop_flag = True
    current_task['status'] = 'stopped'
    return jsonify({'status': 'stopped'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
