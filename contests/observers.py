from decimal import Decimal


class TaskProgressObserver:
    def __init__(self, task):
        self.task = task

    def print(self, *args):
        pass

    def set_progress(self, state, current, total):
        percentage = 0
        if total > 0:
            percentage = (Decimal(current) / Decimal(total)) * Decimal(100)
            percentage = float(round(percentage, 2))
        self.task.update_state(
            state=state,
            meta={
                'current': current,
                'total': total,
                'progress': percentage,
            }
        )
