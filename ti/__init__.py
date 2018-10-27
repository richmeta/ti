#!/usr/bin/env python
# coding: utf-8

"""
ti is a simple and extensible time tracker for the command line. Visit the
project page (http://ti.sharats.me) for more details.

Usage:
  ti (o|on) <name> [<time>...]
  ti (f|fin) [<time>...]
  ti (s|status)
  ti (t|tag) <tag>...
  ti (n|note) <note-text>...
  ti (l|log) [today|yyyy-mm-dd]
  ti (e|edit)
  ti (i|interrupt)
  ti --no-color
  ti -h | --help

Options:
  -h --help         Show this help.
  <start-time>...   A time specification (goto http://ti.sharats.me for more on
                    this).
  <tag>...          Tags can be made of any characters, but its probably a good
                    idea to avoid whitespace.
  <note-text>...    Some arbitrary text to be added as `notes` to the currently
                    working project.
"""

from __future__ import print_function
from __future__ import unicode_literals

import json
import os
import re
import subprocess
import sys
import tempfile
import argparse
from datetime import datetime, timedelta
from collections import defaultdict
from os import path
import yaml


NOW = datetime.now().replace(second=0, microsecond=0)


class TIError(Exception):
    """Errors raised by TI."""


class AlreadyOn(TIError):
    """Already working on that task."""


class NoEditor(TIError):
    """No $EDITOR set."""


class InvalidYAML(TIError):
    """No $EDITOR set."""


class NoTask(TIError):
    """Not working on a task yet."""


class BadTime(TIError):
    """Time string can't be parsed."""


class JsonStore(object):

    def __init__(self, filename):
        self.filename = filename

    def load(self):

        if path.exists(self.filename):
            with open(self.filename) as f:
                data = json.load(f)

        else:
            data = {'work': [], 'interrupt_stack': []}

        return data

    def dump(self, data):
        with open(self.filename, 'w') as f:
            json.dump(data, f, separators=(',', ': '), indent=2)


def action_on(name, time):
    data = STORE.load()
    work = data['work']
    if work and 'end' not in work[-1]:
        raise AlreadyOn("You are already working on %s. Stop it or use a "
                        "different sheet." % (work[-1]['name'],))

    entry = {
        'name': name,
        'start': NOW.strftime("%Y-%m-%d") + " " + time,
    }

    work.append(entry)
    STORE.dump(data)

    print('Start working on ' + name + '.')


def action_fin(time, back_from_interrupt=True):
    ensure_working()

    data = STORE.load()

    current = data['work'][-1]
    current['end'] = NOW.strftime("%Y-%m-%d") + " " + time
    STORE.dump(data)
    print('So you stopped working on ' + current['name'] + '.')

    if back_from_interrupt and len(data['interrupt_stack']) > 0:
        name = data['interrupt_stack'].pop()['name']
        STORE.dump(data)
        action_on(name, time)
        if len(data['interrupt_stack']) > 0:
            print('You are now %d deep in interrupts.'
                  % len(data['interrupt_stack']))
        else:
            print('Congrats, you\'re out of interrupts!')


def action_interrupt(name, time):
    ensure_working()

    action_fin(time, back_from_interrupt=False)

    data = STORE.load()
    if 'interrupt_stack' not in data:
        data['interrupt_stack'] = []
    interrupt_stack = data['interrupt_stack']

    interrupted = data['work'][-1]
    interrupt_stack.append(interrupted)
    STORE.dump(data)

    action_on('interrupt: ' + name, time)
    print('You are now %d deep in interrupts.' % len(interrupt_stack))


def action_note(content):
    ensure_working()

    data = STORE.load()
    current = data['work'][-1]

    if 'notes' not in current:
        current['notes'] = [content]
    else:
        current['notes'].append(content)

    STORE.dump(data)

    print('Yep, noted to ' + current['name'] + '.')


def action_tag(tags):
    ensure_working()

    data = STORE.load()
    current = data['work'][-1]
    current['tags'] = set(current.get('tags') or [])

    for tag in tags.split(","):
        current['tags'].add(tag)
    current['tags'] = list(current['tags'])

    STORE.dump(data)

    tag_count = len(tags.split(","))
    print("Okay, tagged current work with %d tag%s."
          % (tag_count, "s" if tag_count > 1 else ""))


def action_status():
    ensure_working()

    data = STORE.load()
    current = data['work'][-1]

    start_time = parse_isotime(current['start'])

    print('You have been working on {0} since {1}.'.format(
        current['name'], start_time.strftime("%H:%M")))


def action_log(startdate, enddate):
    data = STORE.load()
    work = data['work'] + data['interrupt_stack']
    log = defaultdict(lambda: {'delta': timedelta()})
    current = None
    for item in work:
        start_time = parse_isotime(item['start'])
        if "end" not in item:
            end_time = NOW
            current = item["name"]
        else:
            end_time = parse_isotime(item['end'])
        if (end_time.date() >= startdate.date()
                and start_time.date() <= enddate.date()):
            log[item['name']]['delta'] += (
                end_time - start_time)

    name_col_len = 0

    for name, item in log.items():
        name_col_len = max(name_col_len, len(name))

        secs = item['delta'].total_seconds()
        tmsg = []

        if secs > 3600:
            hours = int(secs // 3600)
            secs -= hours * 3600
            tmsg.append(str(hours) + ' hour' + ('s' if hours > 1 else ''))

        if secs > 60:
            mins = int(secs // 60)
            secs -= mins * 60
            tmsg.append(str(mins) + ' minute' + ('s' if mins > 1 else ''))

        log[name]['tmsg'] = ', '.join(tmsg)[::-1].replace(',', '& ', 1)[::-1]

    for name, item in sorted(log.items(), key=(lambda x: x[0]), reverse=True):
        print(name.ljust(name_col_len), ' ∙∙ ', item['tmsg'],
              end=' ← working\n' if current == name else '\n')


def action_edit():
    if "EDITOR" not in os.environ:
        raise NoEditor("Please set the 'EDITOR' environment variable")

    data = STORE.load()
    yml = yaml.safe_dump(data, default_flow_style=False, allow_unicode=True)

    cmd = os.getenv('EDITOR')
    fd, temp_path = tempfile.mkstemp(prefix='ti.')
    with open(temp_path, "r+") as f:
        f.write(yml.replace('\n- ', '\n\n- '))
        f.seek(0)
        subprocess.check_call(cmd + ' ' + temp_path, shell=True)
        yml = f.read()
        f.truncate()
        f.close

    os.close(fd)
    os.remove(temp_path)

    try:
        data = yaml.load(yml)
    except (yaml.scanner.ScannerError,
            yaml.parser.ParserError):
        raise InvalidYAML("Oops, that YAML doesn't appear to be valid!")

    STORE.dump(data)


def is_working():
    data = STORE.load()
    return data.get('work') and 'end' not in data['work'][-1]


def ensure_working():
    if is_working():
        return

    raise NoTask("For all I know, you aren't working on anything. "
                 "I don't know what to do.\n"
                 "See `ti -h` to know how to start working.")


def to_datetime(timestr):
    return parse_engtime(timestr).strftime('%Y-%m-%d %H:%M')


def parse_engtime(timestr):

    if not timestr or timestr.strip() == 'now':
        return NOW

    match = re.match(r'(\d+|a) \s* (mins?|minutes?) \s+ ago $', timestr, re.X)
    if match is not None:
        n = match.group(1)
        minutes = 1 if n == 'a' else int(n)
        return NOW - timedelta(minutes=minutes)

    match = re.match(r'(\d+|a|an) \s* (hrs?|hours?) \s+ ago $', timestr, re.X)
    if match is not None:
        n = match.group(1)
        hours = 1 if n in ['a', 'an'] else int(n)
        return NOW - timedelta(hours=hours)

    raise BadTime("Don't understand the time %r" % (timestr,))


def parse_isotime(isotime):
    return datetime.strptime(isotime, '%Y-%m-%d %H:%M')


def validate_time(s):
    try:
        return datetime.strptime(s, "%H:%M")
    except ValueError:
        msg = "Not a valid time hh:mm: '{0}'.".format(s)
        raise argparse.ArgumentTypeError(msg)


def validate_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        msg = "Not a valid date yyyy-mm-dd: '{0}'. U".format(s)
        raise argparse.ArgumentTypeError(msg)


def parse_args():
    parser = argparse.ArgumentParser(description="ti is a simple and "
                                     + "extensible time tracker for the"
                                     + "command line.", prog="ti")
    parser.add_argument("-o", "--on", action="store",
                        help="start an action to work on")
    parser.add_argument("--at", action="store", help="start or stop actions at"
                        + "special time",
                        default=datetime.now().strftime("%H:%M"),
                        type=validate_time)
    parser.add_argument("-l", "--log", action="store_true",
                        help="show log", default=False)
    parser.add_argument("--start", action="store",
                        help="show log from",
                        default=datetime.now().strftime("%Y-%m-%d"),
                        type=validate_date)
    parser.add_argument("--end", action="store",
                        help="show log from",
                        default=datetime.now().strftime("%Y-%m-%d"),
                        type=validate_date)
    parser.add_argument("-f", "--fin", action="store_true",
                        help="end an action")
    parser.add_argument("-t", "--tag", action="store",
                        help="at commasaperated tags to current task")
    parser.add_argument("-s", "--status", action="store_true",
                        help="show status", default=False)
    parser.add_argument("-e", "--edit", action="store_true",
                        help="show status", default=False)
    parser.add_argument("-i", "--interrupt", action="store",
                        help="interrupt the current task with a new tas.")
    parser.add_argument("--note", action="store",
                        help="add a note to the current task")

    arguments = parser.parse_args()
    print(arguments)
    if arguments.on:
        fn = action_on
        args = {
            'name': arguments.on,
            'time': str(arguments.at.hour) + ":" + str(arguments.at.minute)
        }
    if arguments.interrupt:
        fn = action_interrupt
        args = {
            'name': arguments.interrupt,
            'time': str(arguments.at.hour) + ":" + str(arguments.at.minute)
        }

    elif arguments.log:
        fn = action_log
        args = {
            'startdate': arguments.start,
            'enddate': arguments.end
        }
    elif arguments.fin:
        fn = action_fin
        print(arguments.fin)
        args = {
            'time': str(arguments.at.hour) + ":" + str(arguments.at.minute)
        }
    elif arguments.tag:
        fn = action_tag
        args = {
            'tags': str(arguments.tag)
        }
    elif arguments.status:
        fn = action_status
        args = {}
    elif arguments.edit:
        fn = action_edit
        args = {}
    elif arguments.note:
        fn = action_note
        args = {'content': arguments.note}
    else:
        parser.print_help

    return fn, args


def main():

    try:
        fn, args = parse_args()
        fn(**args)
    except TIError as e:
        msg = str(e) if len(str(e)) > 0 else __doc__
        print(msg, file=sys.stderr)
        sys.exit(1)


STORE = JsonStore(os.getenv('SHEET_FILE', None) or
                  os.path.expanduser('~/.ti-sheet'))

if __name__ == '__main__':
    main()
