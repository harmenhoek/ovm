from django.template.defaulttags import register
# from datetime import datetime, timedelta
import datetime
from django.template.defaultfilters import date, timesince
from django.utils.translation import gettext

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def nonetosecondary(value):
    if value:
        return value
    else:
        return "secondary"

@register.filter
def nonetounknown(value):
    if value:
        return value
    else:
        return "<i class='text-muted'>onbekend</i>"

@register.filter
def noneto_description(value):
    if value:
        return value
    else:
        return "<i class='text-muted'>geen omschrijving</i>"




@register.filter('humanized_timesince')
def humanized_timesince_filter(value, arg=None):
    # https: // gist.github.com / jsoa / 4017107
    if not value:
        return u''
    compare_to = type(arg) == datetime and arg or datetime.now()
    one_day = compare_to - timedelta(hours=24)
    two_days = compare_to - timedelta(hours=48)
    week = compare_to - timedelta(days=7)

    func, args = timesince, (value, compare_to)
    if one_day < value < compare_to:
        args = (value, compare_to)
    elif two_days < value < compare_to:
        return gettext('yesterday')
    elif week < value < compare_to:
        func = date
        args = (value, 'l')
    return func(*args)