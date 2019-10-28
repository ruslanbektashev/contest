from django.contrib.auth.models import User

from contest.celery import app
from contests.observers import TaskProgressObserver
from contests.models import Submission


@app.task(bind=True, time_limit=600)
def evaluate_submission(self, submission_id, user_id):
    submission = Submission.objects.get(id=submission_id)
    user = User.objects.get(id=user_id)
    observer = TaskProgressObserver(self)
    submission.evaluate(user, observer)
    return submission.status, submission.get_status_display()
