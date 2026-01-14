from celery import Celery
from app.core.config import settings
import os

# Create Celery instance
celery_app = Celery('webspc_ai')

# Configure Celery
celery_app.conf.update(
    broker_url=f"redis://{settings.redis_celery_host}:{settings.redis_celery_port}/3",  # Using Redis DB 3 for Celery broker
    result_backend=f"redis://{settings.redis_celery_host}:{settings.redis_celery_port}/4",  # Using Redis DB 4 for results
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Shanghai',
    enable_utc=False,
    task_routes={
        'app.tasks.alarm_analysis.analyze_alarm_and_notify_task': {'queue': 'alarm_analysis_queue'},
    },
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)

# Import the alarm_analysis module to ensure tasks are registered
from . import alarm_analysis

# Auto-discover tasks
celery_app.autodiscover_tasks(['app.tasks'])