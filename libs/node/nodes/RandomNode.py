from libs.network.Network import Network, Message
from libs.node.nodes.AbstractNode import AbstractNode
from libs.RepeatedTimer import RepeatedTimer
from libs.node.NodeConfig import NodeConfig

from dataclasses import dataclass
from globals import globals
from random import random

import math
import json




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
        super().__init__(network, node_id, channel)
        self.repeated_timer = RepeatedTimer(config.measurement_interval, self.send_measurement)
        self.config = config

    def send_measurement(self):
        temp = random() * 5 + 17.5
        light = math.floor(random() * 1000)

        self.send_message(0xFF, str(Measurement(
            temp, light
        )), 0xFF)

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