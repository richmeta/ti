# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

import yaml
import os
import subprocess
import sys
import tempfile
from datetime import timedelta
from collections import defaultdict
from ti.colors import red, yellow, green
from ti.utils import datetime, parse_isotime, timegap
from ti import store


def action_on(name, time):
    data = store.load()
    work = data['work']

    if work and 'end' not in work[-1]:
        print('You are already working on ' + yellow(work[-1]['name']) +
              '. Stop it or use a different sheet.', file=sys.stderr)
        raise SystemExit(1)

    entry = {
        'name': name,
        'start': time,
    }

    work.append(entry)
    store.dump(data)

    print('Start working on ' + green(name) + '.')


def action_fin(time, back_from_interrupt=True):
    ensure_working()

    data = store.load()

    current = data['work'][-1]
    current['end'] = time
    store.dump(data)
    print('So you stopped working on ' + red(current['name']) + '.')

    if back_from_interrupt and len(data['interrupt_stack']) > 0:
        name = data['interrupt_stack'].pop()['name']
        store.dump(data)
        action_on(name, time)
        if len(data['interrupt_stack']) > 0:
            print('You are now %d deep in interrupts.'
                  % len(data['interrupt_stack']))
        else:
            print('Congrats, you\'re out of interrupts!')


def action_interrupt(name, time):
    ensure_working()

    action_fin(time, back_from_interrupt=False)

    data = store.load()
    if 'interrupt_stack' not in data:
        data['interrupt_stack'] = []
    interrupt_stack = data['interrupt_stack']

    interrupted = data['work'][-1]
    interrupt_stack.append(interrupted)
    store.dump(data)

    action_on('interrupt: ' + green(name), time)
    print('You are now %d deep in interrupts.' % len(interrupt_stack))


def action_note(content):
    ensure_working()

    data = store.load()
    current = data['work'][-1]

    if 'notes' not in current:
        current['notes'] = [content]
    else:
        current['notes'].append(content)

    store.dump(data)

    print('Yep, noted to ' + yellow(current['name']) + '.')


def action_tag(tags):
    ensure_working()

    data = store.load()
    current = data['work'][-1]

    current['tags'] = set(current.get('tags') or [])
    current['tags'].update(tags)
    current['tags'] = list(current['tags'])

    store.dump(data)

    tag_count = str(len(tags))
    print('Okay, tagged current work with ' + tag_count + ' tag' +
          ('s' if tag_count > 1 else '') + '.')


def action_status():
    try:
        ensure_working()
    except SystemExit(1):
        return

    data = store.load()
    current = data['work'][-1]

    start_time = parse_isotime(current['start'])
    diff = timegap(start_time, datetime.utcnow())

    print('You have been working on {0} for {1}.'.format(
        green(current['name']), diff))


def action_log(period):
    data = store.load()
    work = data['work'] + data['interrupt_stack']
    log = defaultdict(lambda: {'delta': timedelta()})
    current = None
    name_col_len = 0

    for item in work:
        start_time = parse_isotime(item['start'])
        if 'end' in item:
            log[item['name']]['delta'] += (
                parse_isotime(item['end']) - start_time)
        else:
            log[item['name']]['delta'] += datetime.utcnow() - start_time
            current = item['name']

    for name, item in log.items():
        name_col_len = max(name_col_len, len(name))

        secs = item['delta'].seconds
        tmsg = []

        if secs > 3600:
            hours = int(secs / 3600)
            secs -= hours * 3600
            tmsg.append(str(hours) + ' hour' + ('s' if hours > 1 else ''))

        if secs > 60:
            mins = int(secs / 60)
            secs -= mins * 60
            tmsg.append(str(mins) + ' minute' + ('s' if mins > 1 else ''))

        if secs:
            tmsg.append(str(secs) + ' second' + ('s' if secs > 1 else ''))

        log[name]['tmsg'] = ', '.join(tmsg)[::-1].replace(',', '& ', 1)[::-1]

    log_list = []
    for name, item in log.items():
        log_list.append(
            (
                name,
                item['delta'],
                item['tmsg']
            )
        )
    for name, delta, tmsg in sorted(log_list, key=lambda x: x[0], reverse=True):
        print(name.ljust(name_col_len), ' ∙∙ ', tmsg,
              end=' ← working\n' if current == name else '\n')


def action_edit():
    if 'EDITOR' not in os.environ:
        print("Please set the 'EDITOR' environment variable", file=sys.stderr)
        raise SystemExit(1)

    data = store.load()
    yml = yaml.safe_dump(data, default_flow_style=False, allow_unicode=True)

    cmd = os.getenv('EDITOR')
    fd, temp_path = tempfile.mkstemp(prefix='ti.')
    with open(temp_path, "r+") as f:
        f.write(yml.replace('\n- ', '\n\n- '))
        f.seek(0)
        subprocess.check_call(cmd + ' ' + temp_path, shell=True)
        yml = f.read()
        f.truncate()
        f.close()

    os.close(fd)
    os.remove(temp_path)

    try:
        data = yaml.load(yml)
    except:
        print("Oops, that YAML didn't appear to be valid!", file=sys.stderr)
        raise SystemExit(1)

    store.dump(data)


def is_working():
    data = store.load()
    return data.get('work') and 'end' not in data['work'][-1]


def ensure_working():
    if is_working():
        return

    print("For all I know, you aren't working on anything. "
          "I don't know what to do.", file=sys.stderr)
    print('See `ti -h` to know how to start working.', file=sys.stderr)
    raise SystemExit(1)
