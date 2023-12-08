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