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
  ti (l|log) [today]
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

import sys
from .actions import action_edit, action_fin, action_interrupt, action_log, action_note, action_on, \
    action_status, action_tag
from .utils import to_datetime


def helpful_exit(msg=__doc__):
    print(msg, file=sys.stderr)
    raise SystemExit


def parse_args(argv=sys.argv):
    use_color = False

    argv = [arg for arg in argv]

    if '--no-color' in argv:
        use_color = False
        argv.remove('--no-color')

    # prog = argv[0]
    if len(argv) == 1:
        helpful_exit('You must specify a command.')

    head = argv[1]
    tail = argv[2:]

    if head in ['-h', '--help', 'h', 'help']:
        helpful_exit()

    elif head in ['e', 'edit']:
        fn = action_edit
        args = {}

    elif head in ['o', 'on']:
        if not tail:
            helpful_exit('Need the name of whatever you are working on.')

        fn = action_on
        args = {
            'name': tail[0],
            'time': to_datetime(' '.join(tail[1:])),
        }

    elif head in ['f', 'fin']:
        fn = action_fin
        args = {'time': to_datetime(' '.join(tail))}

    elif head in ['s', 'status']:
        fn = action_status
        args = {}

    elif head in ['l', 'log']:
        fn = action_log
        args = {'period': tail[0] if tail else None}

    elif head in ['t', 'tag']:
        if not tail:
            helpful_exit('Please provide at least one tag to add.')

        fn = action_tag
        args = {'tags': tail}

    elif head in ['n', 'note']:
        if not tail:
            helpful_exit('Please provide some text to be noted.')

        fn = action_note
        args = {'content': ' '.join(tail)}

    elif head in ['i', 'interrupt']:
        if not tail:
            helpful_exit('Need the name of whatever you are working on.')

        fn = action_interrupt
        args = {
            'name': tail[0],
            'time': to_datetime(' '.join(tail[1:])),
        }

    else:
        helpful_exit("I don't understand '" + head + "'")

    return fn, args


def main():
    fn, args = parse_args()
    fn(**args)


if __name__ == '__main__':
    main()
