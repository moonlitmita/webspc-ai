#Copyright 2025-present Yu Wang. All Rights Reserved.
#
#Distributed under MIT license.
#See file LICENSE for detail or copy at https://opensource.org/licenses/MIT

import os
import sys
from app.tasks import celery_app

if __name__ == '__main__':
    # Set the default configuration for Celery
    os.environ.setdefault('FORKED_BY_MULTIPROCESSING', '1')
    
    # Start the Celery worker
    celery_app.start(argv=sys.argv)