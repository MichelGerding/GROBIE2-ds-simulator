import json
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
        return json.dumps({
            'temp': self.temp,
            'light': self.light,
            'datetime': self.datetime.timestamp()
        }, sort_keys=True)

    @staticmethod
    def deserialize(data: str):
        """ deserialize a string to a measurement """
        data = json.loads(data)
        return Measurement(
            temp=data['temp'],
            light=data['light']
        )

    def serialize(self):
        """ serialize a measurement to a string """
        return json.dumps(self.__dict__, sort_keys=True)
