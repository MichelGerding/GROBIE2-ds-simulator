import os
import sys

from datetime import datetime

class Logger:
    def __init__(self, filename):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        self.file = open(filename, 'w')
        self.stout = sys.stdout

    def write(self, obj):
        if obj != '\n':
            self.file.write(f'{datetime.now()}> {obj}\n')
            self.file.flush()

        self.stout.write(obj)
        self.stout.flush()
    def flush(self):
        self.stout.flush()
        self.file.flush()
