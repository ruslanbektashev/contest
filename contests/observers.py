from decimal import Decimal


class TaskProgressObserver:
    def __init__(self, task):
        self.task = task

    def print(self, *args):
        pass

    def set_progress(self, state, current, total):
        percent = 0
        if total > 0:
            percent = (Decimal(current) / Decimal(total)) * Decimal(100)
            percent = float(round(percent, 2))
        self.task.update_state(
            state=state,
            meta={
                'current': current,
                'total': total,
                'percent': percent,
            }
        )
