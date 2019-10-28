import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contest.settings')

app = Celery('contest')

app.conf.update(result_backend='rpc://', task_track_started=True)

app.autodiscover_tasks()
