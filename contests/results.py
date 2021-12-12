from celery.result import AsyncResult

from contests.templatetags.contests import colorize


class TaskProgress:
    def __init__(self, task_id):
        if not isinstance(task_id, str):
            raise ValueError("task_id must be a string")
        self.result = AsyncResult(task_id)

    def get_info(self):
        if self.result.ready():
            status, status_display = self.result.get()
            return {
                'state': self.result.state,
                'result': status_display,
                'class': colorize(status),
                'complete': True,
                'success': self.result.successful()
            }
        elif self.result.state in ['PENDING', 'STARTED']:
            return {
                'state': self.result.state,
                'progress': 0,
                'complete': False,
                'success': None
            }
        progress = 0
        try:
            progress = self.result.info.get('progress', 0)
        except AttributeError:
            pass
        return {
            'state': self.result.state,
            'progress': progress,
            'complete': False,
            'success': None
        }