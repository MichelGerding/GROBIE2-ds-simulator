import os

class Logger:
    def __init__(self, filename):
        self.filename = filename
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        self.file = open(filename, 'w')

    def log(self, msg):
        self.file.write(msg + '\n')
        self.file.flush()

    def print(self, msg):
        print(msg)
        self.log(msg)