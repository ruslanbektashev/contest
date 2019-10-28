from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.db.models import QuerySet

from .models import Activity


def activity_handler(**kwargs):
    """ handler function to create Activity instance upon notification signal call. """
    kwargs.pop('signal', None)
    subject = kwargs.pop('sender')
    recipient = kwargs.pop('recipient')
    action = kwargs.pop('action')
    object = kwargs.pop('object', None)
    reference = kwargs.pop('reference', None)
    level = kwargs.pop('level', None)
    date_created = kwargs.pop('date_created', None)
    if isinstance(recipient, Group):
        recipients = recipient.user_set.all()
    elif isinstance(recipient, QuerySet) or isinstance(recipient, list):
        recipients = recipient
    else:
        recipients = [recipient]
    optional = dict()
    if level:
        optional['level'] = level
    if date_created:
        optional['date_created'] = date_created
    new_activities = []
    for recipient in recipients:
        activity = Activity(subject_type=ContentType.objects.get_for_model(subject),
                            subject_id=subject.id,
                            recipient=recipient,
                            action=action,
                            **optional)
        if object:
            activity.object_type = ContentType.objects.get_for_model(object)
            activity.object_id = object.id
        if reference:
            activity.reference_type = ContentType.objects.get_for_model(reference)
            activity.reference_id = reference.id
        new_activities.append(activity)
    return Activity.objects.bulk_create(new_activities)
