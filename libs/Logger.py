import os
import sys

from datetime import datetime

class Logger:
    def __init__(self, filename):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        self.file = open(filename, 'w')
        self.stout = sys.stdout

    def write(self, obj):
        self.stout.write(obj)
        self.file.write(f'{datetime.now()}> {obj}\n')
        self.file.flush()

    def flush(self):
        self.stout.flush()
        self.file.flush()
