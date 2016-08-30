# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

# import re
# from datetime import datetime, timedelta
import pendulum
import math


# def to_datetime(timestr):
#     return parse_engtime(timestr).isoformat() + 'Z'
#
#
# def parse_engtime(timestr):
#
#     now = datetime.utcnow()
#     if not timestr or timestr.strip() == 'now':
#         return now
#
#     match = re.match(r'(\d+|a) \s* (s|secs?|seconds?) \s+ ago $',
#                      timestr, re.X)
#     if match is not None:
#         n = match.group(1)
#         seconds = 1 if n == 'a' else int(n)
#         return now - timedelta(seconds=seconds)
#
#     match = re.match(r'(\d+|a) \s* (mins?|minutes?) \s+ ago $', timestr, re.X)
#     if match is not None:
#         n = match.group(1)
#         minutes = 1 if n == 'a' else int(n)
#         return now - timedelta(minutes=minutes)
#
#     match = re.match(r'(\d+|a|an) \s* (hrs?|hours?) \s+ ago $', timestr, re.X)
#     if match is not None:
#         n = match.group(1)
#         hours = 1 if n in ['a', 'an'] else int(n)
#         return now - timedelta(hours=hours)
#
#     raise ValueError("Don't understand the time '" + timestr + "'")
#
#
# def parse_isotime(isotime):
#     return datetime.strptime(isotime, '%Y-%m-%dT%H:%M:%S.%fZ')
#
#
# def timegap(start_time, end_time):
#     diff = end_time - start_time
#
#     mins = diff.seconds / 60
#
#     if mins == 0:
#         return 'less than a minute'
#     elif mins == 1:
#         return 'a minute'
#     elif mins < 44:
#         return '{} minutes'.format(mins)
#     elif mins < 89:
#         return 'about an hour'
#     elif mins < 1439:
#         return 'about {} hours'.format(mins / 60)
#     elif mins < 2519:
#         return 'about a day'
#     elif mins < 43199:
#         return 'about {} days'.format(mins / 1440)
#     elif mins < 86399:
#         return 'about a month'
#     elif mins < 525599:
#         return 'about {} months'.format(mins / 43200)
#     else:
#         return 'more than a year'


def seconds_to_hours_and_minutes(seconds):
    ceil_seconds = math.ceil(seconds/60)*60
    interval = pendulum.interval(seconds=ceil_seconds)

    if interval.total_hours() > 24:
        hours = math.floor(interval.total_hours())
        minutes = interval.minutes
        if minutes > 1:
            return '{} hours {} minutes'.format(hours, minutes)
        else:
            return '{} hours {} minute'.format(hours, minutes)

    return interval.__str__()
