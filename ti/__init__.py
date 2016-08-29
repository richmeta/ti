# coding: utf-8
import os
import json

__version__ = '0.1.1.dev1'


class JsonStore(object):

    def __init__(self, filename):
        self.filename = filename

    def load(self):

        if os.path.exists(self.filename):
            with open(self.filename) as f:
                data = json.load(f)

        else:
            data = {'work': [], 'interrupt_stack': []}

        return data

    def dump(self, data):
        with open(self.filename, 'w') as f:
            json.dump(data, f, separators=(',', ': '), indent=2)


store = JsonStore(os.getenv('SHEET_FILE', None) or os.path.expanduser('~/.ti-sheet'))
