import datetime

from django import template
from django.utils import timezone

register = template.Library()


def iso_to_gregorian(year, week, day):
    """Gregorian calendar date for the given ISO year, week and day"""
    fourth_jan = datetime.date(year, 1, 4)
    _, fourth_jan_week, fourth_jan_day = fourth_jan.isocalendar()
    return fourth_jan + datetime.timedelta(days=day - fourth_jan_day, weeks=week - fourth_jan_week)


@register.inclusion_tag('contests/event/event_schedule_weekly.html', takes_context=True)
def render_schedule_weekly(context, year, week, events):
    date_week_start, date_week_end = iso_to_gregorian(year, week, 1), iso_to_gregorian(year, week, 7)
    week = {
        'date_week_start': date_week_start,
        'date_week_end': date_week_end,
        'number': week,
        'days': []
    }
    for d in range(7):
        date_day = date_week_start + datetime.timedelta(days=d)
        day = {
            'date_day': date_day,
            'rows': []
        }
        for h, m, dur in ((9, 00, 90), (10, 45, 90), (13, 15, 90), (15, 00, 90), (16, 45, 90), (18, 30, 90)):
            date_row_start = datetime.datetime.combine(date_day, datetime.time(h, m))
            row = {
                'date_row_start': date_row_start,
                'date_row_end': date_row_start + datetime.timedelta(minutes=90),
                'event': None
            }
            day['rows'].append(row)
        week['days'].append(day)
    i = len(events) - 1
    for day in week['days']:
        for row in day['rows']:
            row_start = timezone.make_aware(row['date_row_start'])
            row_end = timezone.make_aware(row['date_row_end'])
            while i > 0 and events[i].date_start < row_start:
                i -= 1
            while i >= 0 and row_start <= events[i].date_start <= row_end:
                row['event'] = events[i]
                i -= 1
        while i > 0 and day['date_day'] == events[i].date_start.date():
            i -= 1
    context['week'] = week
    return context
