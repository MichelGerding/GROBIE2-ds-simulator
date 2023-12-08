# the code in this file is taken from the following stack overflow answer:
# https://stackoverflow.com/a/38317060
# the code has some adjustments made. for example the timer is now a daemon thread. and won't start on init.

from threading import Timer


class RepeatedTimer(object):
    """ RepeatedTimer class.
        this class wil manage a task on a separate thread that will run every interval seconds.
        the task will run in a separate thread, so it will not block the main thread.
        the thread needs to be started with the start() method. otherwise it will not run.
        the thread can be stopped with the stop() method. """

    def __init__(self, interval, function, *args, **kwargs):
        self._timer = None
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.is_running = False

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        """ start the task """
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.daemon = True
            self._timer.start()
            self.is_running = True

    def stop(self):
        """ stop the task """
        if self._timer:
            self._timer.cancel()
        self.is_running = False
