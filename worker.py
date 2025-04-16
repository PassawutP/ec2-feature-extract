from celery import Celery

# Initialize Celery
celery_app = Celery('tasks', broker='redis://localhost:6379/0')

# Import your tasks here
from app.tasks import process_urls_task

# Optionally, ensure that Celery knows about the tasks
celery_app.conf.task_routes = {
    'app.tasks.process_urls_task': {'queue': 'default'},
}
