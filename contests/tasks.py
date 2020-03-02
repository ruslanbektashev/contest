import mosspy

from billiard.exceptions import SoftTimeLimitExceeded

from django.contrib.auth.models import User

from contest.celery import app
from contests.observers import TaskProgressObserver
from contests.models import Submission
from tools.utility import Status


@app.task(bind=True, soft_time_limit=600, time_limit=660)
def evaluate_submission(self, submission_id, user_id):
    submission = Submission.objects.get(id=submission_id)
    user = User.objects.get(id=user_id)

    observer = TaskProgressObserver(self)
    try:
        submission.evaluate(user, observer)
    except SoftTimeLimitExceeded:
        submission.update(Status.TL)

    return submission.status, submission.get_status_display()


@app.task(bind=True, time_limit=600)
def moss_submission(self, submission_id, to_submission_ids):
    submission = Submission.objects.get(id=submission_id)
    to_submissions = Submission.objects.filter(id__in=to_submission_ids)

    lang_opt = {'C': 'c', 'C++': 'cc'}
    moss = mosspy.Moss(427263405, lang_opt[submission.problem.language])
    for path in submission.files:
        moss.addFile(path, str(submission.id))
    for to_submission in to_submissions:
        for path in to_submission.files:
            moss.addFile(path, str(to_submission.id))
    report_url = moss.send()

    submission.moss_report_url = report_url
    submission.save()
