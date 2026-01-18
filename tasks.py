"""
Task Queue System for NexoraMsg
Manages background sending tasks with proper state management
"""

from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
import threading
from queue import Queue, PriorityQueue
import uuid

class TaskStatus(Enum):
    """Task lifecycle states"""
    IDLE = "idle"
    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    STOPPED = "stopped"

class TaskPriority(Enum):
    """Task priority levels"""
    LOW = 3
    NORMAL = 2
    HIGH = 1

@dataclass
class Message:
    """Individual message record"""
    recipient: str
    platform: str
    status: str = "pending"  # pending, sent, failed, invalid
    timestamp: Optional[datetime] = None
    delay_used: float = 0.0
    error: Optional[str] = None

@dataclass
class Task:
    """Background task container"""
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    platform: str = "whatsapp"
    recipients: List[str] = field(default_factory=list)
    message: str = ""
    status: TaskStatus = TaskStatus.IDLE
    priority: TaskPriority = TaskPriority.NORMAL
    
    # Progress tracking
    total: int = 0
    current: int = 0
    progress: int = 0
    
    # Timing
    start_time: Optional[datetime] = None
    elapsed: int = 0
    estimated_remaining: int = 0
    
    # Logging
    messages: List[Message] = field(default_factory=list)
    log_file: Optional[str] = None
    
    # Configuration
    min_delay: float = 35.0
    max_delay: float = 180.0
    
    # Thread management
    stop_event: threading.Event = field(default_factory=threading.Event)
    pause_event: threading.Event = field(default_factory=threading.Event)
    
    def to_dict(self):
        """Convert task to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'platform': self.platform,
            'status': self.status.value,
            'total': self.total,
            'current': self.current,
            'progress': self.progress,
            'elapsed': self.elapsed,
            'estimated_remaining': self.estimated_remaining,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'log_file': self.log_file,
            'messages': [
                {
                    'recipient': m.recipient,
                    'status': m.status,
                    'timestamp': m.timestamp.isoformat() if m.timestamp else None,
                    'delay_used': m.delay_used,
                    'error': m.error
                }
                for m in self.messages[-10:]  # Last 10 messages
            ]
        }


class TaskQueue:
    """Thread-safe task queue with priority support"""
    
    def __init__(self, max_workers: int = 1):
        self.queue: PriorityQueue = PriorityQueue()
        self.active_task: Optional[Task] = None
        self.completed_tasks: List[Task] = []
        self.max_workers = max_workers
        self.lock = threading.RLock()
        
    def add_task(self, task: Task, priority: TaskPriority = TaskPriority.NORMAL):
        """Add task to queue"""
        with self.lock:
            task.priority = priority
            self.queue.put((priority.value, task.id, task))
    
    def get_next_task(self) -> Optional[Task]:
        """Get next task from queue"""
        try:
            _, task_id, task = self.queue.get_nowait()
            with self.lock:
                self.active_task = task
            return task
        except:
            return None
    
    def mark_completed(self, task: Task):
        """Mark task as completed"""
        with self.lock:
            task.status = TaskStatus.COMPLETED
            self.completed_tasks.append(task)
            self.active_task = None
    
    def mark_failed(self, task: Task, error: str):
        """Mark task as failed"""
        with self.lock:
            task.status = TaskStatus.FAILED
            self.completed_tasks.append(task)
            self.active_task = None
    
    def get_active_task(self) -> Optional[Task]:
        """Get currently active task"""
        with self.lock:
            return self.active_task
    
    def pause_task(self):
        """Pause active task"""
        if self.active_task:
            self.active_task.status = TaskStatus.PAUSED
            self.active_task.pause_event.set()
    
    def resume_task(self):
        """Resume paused task"""
        if self.active_task:
            self.active_task.status = TaskStatus.RUNNING
            self.active_task.pause_event.clear()
    
    def stop_task(self):
        """Stop active task"""
        if self.active_task:
            self.active_task.status = TaskStatus.STOPPED
            self.active_task.stop_event.set()
    
    def get_queue_size(self) -> int:
        """Get number of tasks in queue"""
        return self.queue.qsize()
    
    def get_stats(self) -> dict:
        """Get queue statistics"""
        with self.lock:
            return {
                'queue_size': self.queue.qsize(),
                'active_task': self.active_task.id if self.active_task else None,
                'completed_count': len(self.completed_tasks),
                'total_messages': sum(len(t.messages) for t in self.completed_tasks)
            }


# Global task queue instance
task_queue = TaskQueue(max_workers=1)


class TaskExecutor:
    """Executes tasks with proper state management"""
    
    def __init__(self, queue: TaskQueue):
        self.queue = queue
        self.worker_threads = []
    
    def start_workers(self, count: int = 1):
        """Start worker threads"""
        for i in range(count):
            thread = threading.Thread(
                target=self._worker_loop,
                name=f"TaskWorker-{i}",
                daemon=True
            )
            thread.start()
            self.worker_threads.append(thread)
    
    def _worker_loop(self):
        """Main worker loop"""
        while True:
            task = self.queue.get_next_task()
            if task:
                self._execute_task(task)
    
    def _execute_task(self, task: Task):
        """Execute a single task"""
        try:
            task.status = TaskStatus.RUNNING
            task.start_time = datetime.now()
            
            # Simulate task execution
            # In real usage, this would call send_whatsapp_messages_with_log or send_telegram_messages_with_log
            
            task.status = TaskStatus.COMPLETED
            self.queue.mark_completed(task)
        except Exception as e:
            self.queue.mark_failed(task, str(e))
