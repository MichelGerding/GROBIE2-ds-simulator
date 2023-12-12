from dataclasses import dataclass

import json


@dataclass
class Measurement:
    """ A measurement contains a temperature and light value.
        This is the data that will be sent to the network."""
    temp: float
    light: int

    def __str__(self):
        return json.dumps({
            'temp': self.temp,
            'light': self.light
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
        return str(self)
