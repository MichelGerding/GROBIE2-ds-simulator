import json
import pickle
from datetime import datetime, timezone

class Measurement:
    """ A measurement contains a temperature and light value.
        This is the data that will be sent to the network."""
    temp: float
    light: int
    datetime: datetime = None

    def __init__(self, temp, light, dt=None):
        self.temp = temp
        self.light = light

        if dt is None:
            # use current time
            dt = datetime.now(timezone.utc)
        self.datetime = dt

    def __str__(self):
        return json.dumps(self.__dict__, sort_keys=True)

    @staticmethod
    def deserialize(data: bytes):
        """ deserialize a string to a measurement """
        return pickle.loads(data)

    def serialize(self):
        """ serialize a measurement to a string """
        return pickle.dumps(self)
