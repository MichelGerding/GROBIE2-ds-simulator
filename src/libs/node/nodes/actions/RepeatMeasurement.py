from libs.network.Measurement import Measurement
from libs.RepeatedTimer import RepeatedTimer

from typing import Callable
from random import random

import math


class RepeatMeasurement:
    """ This class will periodically make measurements. """
    interval: float
    timer: RepeatedTimer
    data_functions: list[Callable[[Measurement], Measurement]]

    def __init__(self, interval, data_functions=None):
        """ interval: the interval at which measurements should be made (once every interval seconds).
            data_modifiers: a list of functions that will be called on the measurement """

        self.interval = interval
        self.timer = RepeatedTimer(self.interval, self.measure)

        if data_functions is None:
            data_functions = []
        self.data_functions = data_functions

    def start(self):
        """ start making measurements """
        self.timer.start()

    def stop(self):
        """ stop making measurements """
        self.timer.stop()

    def change_interval(self, interval):
        """ change the interval at which measurements are made """
        self.timer.stop()
        self.interval = interval
        self.timer = RepeatedTimer(self.interval, self.measure)
        self.timer.start()

    def measure(self):
        """ make a measurement and apply the data modifiers """
        temp = random() * 5 + 17.5
        light = math.floor(random() * 1000)

        m = Measurement(temp, light)

        for modifier in self.data_functions:
            m = modifier(m)
