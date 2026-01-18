from flask import Flask, render_template, request, jsonify, session
from sender import send_whatsapp_messages_with_log, send_telegram_messages_with_log, close_driver
import uuid
import os
import threading
import time
from datetime import datetime
from queue import Queue, Empty
import json

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'nexoramsg-secret-key-2026')

# Task Queue Management
class TaskManager:
    def __init__(self):
        self.tasks = {}
        self.task_queue = Queue()
        self.current_task = None
        self.lock = threading.Lock()
    
    def create_task(self, platform, recipients, message):
        """Create a new sending task"""
        task_id = str(uuid.uuid4())
        task = {
            'id': task_id,
            'platform': platform,
            'total_recipients': len(recipients),
            'recipients': recipients,
            'message': message,
            'status': 'queued',
            'current_index': 0,
            'sent': 0,
            'failed': 0,
            'invalid': 0,
            'start_time': None,
            'end_time': None,
            'current_recipient': None,
            'current_delay': 0,
            'log_file': None,
            'error': None,
            'progress_percent': 0
        }
        with self.lock:
            self.tasks[task_id] = task
        return task_id
    
    def get_task(self, task_id):
        """Get task details"""
        with self.lock:
            return self.tasks.get(task_id, {})
    
    def update_task(self, task_id, **kwargs):
        """Update task status"""
        with self.lock:
            if task_id in self.tasks:
                self.tasks[task_id].update(kwargs)
    
    def get_all_tasks(self):
        """Get all tasks"""
        with self.lock:
            return dict(self.tasks)

# Initialize task manager
task_manager = TaskManager()

# Telegram API token
TELEGRAM_API_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')

def clean_number(num):
    return ''.join(filter(str.isdigit, num))

def send_with_progress(task_id, platform, recipients, message, log_path):
    """Send messages and update progress"""
    task_manager.update_task(task_id, status='running', start_time=datetime.now().isoformat())
    
    try:
        if platform == 'whatsapp':
            send_whatsapp_messages_with_log(
                recipients, message, log_path, append=False, 
                task_manager=task_manager, task_id=task_id
            )
        elif platform == 'telegram':
            send_telegram_messages_with_log(
                recipients, message, log_path, append=False,
                api_token=TELEGRAM_API_TOKEN,
                task_manager=task_manager, task_id=task_id
            )
        
        task_manager.update_task(task_id, status='completed', end_time=datetime.now().isoformat())
    except Exception as e:
        task_manager.update_task(task_id, status='failed', error=str(e), end_time=datetime.now().isoformat())
        print(f"❌ Task {task_id} failed: {e}")
    finally:
        close_driver()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'Stop':
            return render_template('index.html', uploaded=True, status='⛔ Stopped', telegram_token=bool(TELEGRAM_API_TOKEN))

        platform = request.form.get('platform', 'whatsapp')
        recipients_raw = request.form.get('recipients', '')
        message = request.form.get('message', '')

        if not recipients_raw.strip() or not message.strip():
            return render_template('index.html', uploaded=False, error="❌ Please enter recipients and message.", telegram_token=bool(TELEGRAM_API_TOKEN))

        # Clean recipients
        if platform == 'whatsapp':
            recipients = [clean_number(num.strip()) for num in recipients_raw.split('\n') if num.strip()]
        else:
            recipients = [r.strip() for r in recipients_raw.split('\n') if r.strip()]

        if not recipients:
            return render_template('index.html', uploaded=False, error="❌ No valid recipients found.", telegram_token=bool(TELEGRAM_API_TOKEN))

        # Create task
        task_id = task_manager.create_task(platform, recipients, message)
        log_filename = f'{platform}_log_{task_id[:6]}.xlsx'
        log_path = os.path.join('static', 'logs', log_filename)
        os.makedirs('static/logs', exist_ok=True)
        
        task_manager.update_task(task_id, log_file=log_filename)
        
        # Start sending in background
        thread = threading.Thread(target=send_with_progress, args=(task_id, platform, recipients, message, log_path))
        thread.daemon = True
        thread.start()
        
        return render_template('dashboard.html', task_id=task_id, telegram_token=bool(TELEGRAM_API_TOKEN))

    return render_template('index.html', uploaded=False, telegram_token=bool(TELEGRAM_API_TOKEN))

@app.route('/api/task/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """Get real-time task status"""
    task = task_manager.get_task(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    return jsonify({
        'id': task.get('id'),
        'platform': task.get('platform'),
        'status': task.get('status'),
        'total': task.get('total_recipients'),
        'current': task.get('current_index'),
        'sent': task.get('sent'),
        'failed': task.get('failed'),
        'invalid': task.get('invalid'),
        'progress': task.get('progress_percent'),
        'current_recipient': task.get('current_recipient'),
        'current_delay': task.get('current_delay'),
        'log_file': task.get('log_file'),
        'error': task.get('error'),
        'start_time': task.get('start_time'),
        'end_time': task.get('end_time')
    })

@app.route('/api/tasks', methods=['GET'])
def get_all_tasks():
    """Get all tasks"""
    tasks = task_manager.get_all_tasks()
    return jsonify(tasks)

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    """Download log file"""
    return app.send_file(
        os.path.join('static', 'logs', filename),
        as_attachment=True
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
