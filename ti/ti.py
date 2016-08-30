# coding: utf-8
"""
ti is a simple and extensible time tracker for the command line. Visit the
project page (http://ti.sharats.me) for more details.
"""

from __future__ import print_function
from __future__ import unicode_literals
import argparse
import sys
from .actions import Actions
import sys


# def parse_args(argv=sys.argv):
#     use_color = False
#
#     argv = [arg for arg in argv]
#
#     if '--no-color' in argv:
#         use_color = False
#         argv.remove('--no-color')
#
#     # prog = argv[0]
#     if len(argv) == 1:
#         helpful_exit('You must specify a command.')
#
#     head = argv[1]
#     tail = argv[2:]
#
#     elif head in ['e', 'edit']:
#         fn = action_edit
#         args = {}
#
#     elif head in ['t', 'tag']:
#         if not tail:
#             helpful_exit('Please provide at least one tag to add.')
#
#         fn = action_tag
#         args = {'tags': tail}
#
#     elif head in ['n', 'note']:
#         if not tail:
#             helpful_exit('Please provide some text to be noted.')
#
#         fn = action_note
#         args = {'content': ' '.join(tail)}
#
#     elif head in ['i', 'interrupt']:
#         if not tail:
#             helpful_exit('Need the name of whatever you are working on.')
#
#         fn = action_interrupt
#         args = {
#             'name': tail[0],
#             'time': to_datetime(' '.join(tail[1:])),
#         }
#
#     else:
#         helpful_exit("I don't understand '" + head + "'")
#
#     return fn, args


# Inpired by Multi-level argparse by @chase_seibert
# http://chase-seibert.github.io/blog/2014/03/21/python-multilevel-argparse.html
class Ti(object):
    valid_commands = {
        'on': ['o', 'on'],
        'fin': ['f', 'fin'],
        'status': ['s', 'status'],
        'log': ['l', 'log'],
        'report': ['r', 'report'],
    }
    actions = None

    def __init__(self):
        self.actions = Actions()
        parser = argparse.ArgumentParser(
            usage=""" ti <command> [<args>]

ti is a simple and extensible time tracker for the command line.
Visit the project page (http://ti.sharats.me) for more details.

Commands:
  o, on        Start new tracking
  f, fin       Stop currently running tracking
  s, status    Show current status
  l, log       List time logs for period with possible values today (default), week or month
  r, report    Aggregated report for period with possible values today (default), week or month

Old commands:
  ti (t|tag) <tag>...
  ti (n|note) <note-text>...

  ti (e|edit)
  ti (i|interrupt)
  ti --no-color

""")
        parser.add_argument('command', help='Subcommand to run')
        # parse_args defaults to [1:] for args, but you need to
        # exclude the rest of the args too, or validation will fail
        args = parser.parse_args(sys.argv[1:2])

        reverse_map = {}
        for k, v1 in self.valid_commands.items():
            for v2 in v1:
                reverse_map[v2] = k

        if args.command not in reverse_map:
            print('Unrecognized command')
            parser.print_help()
            exit(1)
        getattr(self, reverse_map[args.command])()

    def on(self):
        parser = argparse.ArgumentParser(
            prog='ti on',
            description='Track new task')

        parser.add_argument('task', type=str, nargs="?", help="name of task")
        parser.add_argument('project', type=str, nargs="?", help="group task and tracking under project, "
                                                                 "useful for aggregation")
        parser.add_argument('--ago', type=str, metavar="time",
                            help="shift start of tracking into past, eg. 10 minutes")

        args = parser.parse_args(sys.argv[2:])
        self.actions.action_on(**vars(args))

    def fin(self):
        parser = argparse.ArgumentParser(
            prog='ti fin',
            description='Finish running task')
        parser.add_argument('--ago', type=str, metavar="time",
                            help="shift finish of tracking into past, e.g. 10 minutes")

        args = parser.parse_args(sys.argv[2:])
        self.actions.action_fin(**vars(args))

    def status(self):
        parser = argparse.ArgumentParser(
            prog='ti status',
            description='Get current status')

        args = parser.parse_args(sys.argv[2:])
        self.actions.action_status()

    def log(self):
        parser = argparse.ArgumentParser(
            prog='ti log',
            description='List of time logs for selected period')
        parser.add_argument('period', type=str, metavar="time", nargs="?", default='today',
                            choices=['today', 'week', 'month'],
                            help="period of time, possible choices: today (default), week or month")

        args = parser.parse_args(sys.argv[2:])
        self.actions.action_log(**vars(args))

    def report(self):
        parser = argparse.ArgumentParser(
            prog='ti report',
            description='Aggregated report of time logs for selected period')
        parser.add_argument('period', type=str, metavar="time", nargs="?", default='today',
                            choices=['today', 'week', 'month'],
                            help="period of time, possible choices: today (default), week or month")

        args = parser.parse_args(sys.argv[2:])
        self.actions.action_report(**vars(args))


def main():
    Ti()

if __name__ == '__main__':
    main()
