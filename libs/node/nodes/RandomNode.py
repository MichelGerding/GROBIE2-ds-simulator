from libs.network.Network import Network, Message
from libs.node.nodes.AbstractNode import AbstractNode
from libs.RepeatedTimer import RepeatedTimer
from libs.node.NodeConfig import NodeConfig

from datetime import datetime, timezone
from tinyflux import TinyFlux, Point
from dataclasses import dataclass
from globals import globals
from random import random

import math
import json
import os



# message structure
# type{num 0 - 6} | message


@dataclass
class Measurement:
    temp: float
    light: int

    def __str__(self):
        return json.dumps({
            'temp': self.temp,
            'light': self.light
        }, sort_keys=True)


class RandomNode(AbstractNode):
    """
        This is a node that sends random measurements to the network.
        The rate of measurements can be adjusted by updating the config.
    """
    repeated_timer: RepeatedTimer

    def __init__(self, network: Network, node_id: int, channel: int, config: NodeConfig):
        super().__init__(network, node_id, channel, config)
        self.repeated_timer = RepeatedTimer(config.measurement_interval, self.measure)
        self.config = config

        # setup db
        self.path = f'./tmp/{datetime.now(timezone.utc).timestamp()}_{math.floor(random() * 92121)}_{node_id}.db'

        if not os.path.exists('./tmp'):
            os.mkdir('./tmp')
        print('abs path: ' + os.path.abspath(self.path))

        self.db = TinyFlux(self.path)

    def measure(self):
        temp = random() * 5 + 17.5
        light = math.floor(random() * 1000)

        m = Measurement(temp, light)
        p = Point(
            time=datetime.now(timezone.utc),
            tags={"node": hex(self.node_id)},
            fields={"temp": m.temp, "light": m.light}
        )

        self.db.insert(p)
        self.send_message(0xFF, str(m), 0xFF)

    def handle_message(self, message: Message):
        # check if we send it
        if message.sending_id == self.node_id:
            return

        # check if the message is for us
        if message.receiving_id != 0xFF and message.receiving_id != self.node_id:
            return
        # check if it is the correct channel
        if message.channel != 0xFF and message.channel != self.channel:
            return

        globals['ui'].add_text_to_column2(f'node {self.node_id} got message from node: {message.sending_id}')

        # check if we are replicating this node
        if message.sending_id in [r.node_id for r in self.config.replicating_nodes]:
            m = Measurement(**json.loads(message.message))
            p = Point(
                time=datetime.now(timezone.utc),
                tags={"node": hex(message.sending_id)},
                fields={"temp": m.temp, "light": m.light}
            )

            self.db.insert(p)
            globals['ui'].add_text_to_column2(f'\tnode {self.node_id} replicated node {message.sending_id}')

    def start_measurements(self):
        self.repeated_timer.start()

    def stop_measurements(self):
        self.repeated_timer.stop()

    def change_config(self, key: str, value: str):
        if key == 'measurement_interval':
            self.repeated_timer.stop()
            self.repeated_timer = RepeatedTimer(float(value), self.send_measurement)
            self.config.measurement_interval = float(value)

        if key == 'requested_replications':
            self.config.requested_replications = int(value)
        else:
            print('unknown config key: ', key)
            return

        globals['ui'].add_text_to_column1(f'node {self.node_id} changed config: {key} to {value}', False)
