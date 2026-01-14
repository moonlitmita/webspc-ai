#Copyright 2025-present Yu Wang. All Rights Reserved.
#
#Distributed under MIT license.
#See file LICENSE for detail or copy at https://opensource.org/licenses/MIT

"""
Script to start the Celery worker for alarm analysis tasks
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the project root to the path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.tasks import celery_app

if __name__ == "__main__":
    # Start the Celery worker directly
    celery_app.start([
        "worker",
        "--loglevel=info",
        "--pool=solo",  # Use solo pool to avoid issues with Windows
        "--queues=alarm_analysis_queue"  # Specify the queue to listen to
    ])