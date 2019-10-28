from django.dispatch import Signal

from .utils import activity_handler

notification = Signal(providing_args=['recipient', 'action', 'object', 'reference', 'level', 'date_created'])
notification.connect(activity_handler)
