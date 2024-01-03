from libs.network.Measurement import Measurement

from datetime import datetime, timezone
from tinyflux import TinyFlux, Point, TagQuery
from random import random

import math
import os


class StorageController:

    # TODO:: implement compressions of data
    # TODO:: implement better storage (maybe use sqlite)

    def __init__(self, node_id: int):
        # generate a random file path. this is where the database will be stored.
        # the database used for testing will make use of a csv file for easy reading.
        self.path = f'./tmp/databases/{datetime.now(timezone.utc).timestamp()}_{math.floor(random() * 92121)}_{node_id}.csv'
        os.makedirs(os.path.dirname(self.path), exist_ok=True)

        # create the database
        self.db = TinyFlux(self.path)

    def __call__(self, measurement: Measurement, node_id: int) -> Measurement:
        """ store a measurement in the database """
        self.db.insert(Point(
            time=measurement.datetime,
            tags={"node": hex(node_id)},
            fields={"temp": measurement.temp, "light": measurement.light}
        ))

        return measurement

    def get_data(self, node_id) -> list[Measurement]:
        """ get the data from the database """
        Tag = TagQuery()
        Tag["node"] = hex(node_id)

        res = self.db.search(Tag)
        return [Measurement(dt=point.time, temp=point.fields['temp'], light=point.fields['light']) for point in res]
