import datetime

from django import template

register = template.Library()


def iso_to_gregorian(year, week, day):
    """Gregorian calendar date for the given ISO year, week and day"""
    fourth_jan = datetime.date(year, 1, 4)
    _, fourth_jan_week, fourth_jan_day = fourth_jan.isocalendar()
    return fourth_jan + datetime.timedelta(days=day - fourth_jan_day, weeks=week - fourth_jan_week)
