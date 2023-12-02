from libs.network.Network import Network, Message
from libs.node.nodes.AbstractNode import AbstractNode
from libs.RepeatedTimer import RepeatedTimer
from libs.node.NodeConfig import NodeConfig, ReplicationInfo

from datetime import datetime, timezone
from tinyflux import TinyFlux, Point
from dataclasses import dataclass
from globals import globals
from random import random
from threading import Timer

import math
import json
import os



# message structure
# message

# the channel the message is sent on decides if it is configuration or measurement
# 0xFF is broadcast (not used)
# 0x00 is configuration
# 0x01 is measurement
# 0x02 is node discovery message contains its own configuration
# 0x03 is replication bidding message is hops


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

    ledger: dict[int, NodeConfig] = {}
    replication_bids: dict[int, int] = {}

    def __init__(self, network: Network, node_id: int, channel: int, config: NodeConfig):
        super().__init__(network, node_id, channel, config)
        self.replication_bidding_timer = None
        self.repeated_timer = RepeatedTimer(config.measurement_interval, self.measure)
        self.config = config

        # send discovery message
        self.send_message(0xFF, str(self.config), 0x02)

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
        self.send_message(0xFF, str(m), 0x01)

    def handle_message(self, message: Message):
        """ handle messages that get send to this node.
            This function will only receive messages that are for this node. """

        globals['ui'].add_text_to_column2(f'node {self.node_id} got message from node: {message.sending_id}')

        if message.channel == 0x01:
            globals['ui'].add_text_to_column2(f'\tnode {self.node_id} got measurement from node {message.sending_id}')
            """ handle measurement messages """
            if message.sending_id in [r.node_id for r in self.config.replicating_nodes]:
                m = Measurement(**json.loads(message.message))
                p = Point(
                    time=datetime.now(timezone.utc),
                    tags={"node": hex(message.sending_id)},
                    fields={"temp": m.temp, "light": m.light}
                )

                self.db.insert(p)
                globals['ui'].add_text_to_column2(f'\t\tnode {self.node_id} replicated node {message.sending_id}')

            else:
                # get the nodes config
                config = self.ledger[message.sending_id]
                # check if we need to replicate
                if len(config.replicating_nodes) < config.requested_replications:
                    # send replication bidding message
                    self.send_message(message.sending_id, str("1"), 0x03)

        elif message.channel == 0x00 or message.channel == 0x02:
            """ handle configuration and node discovery messages """
            globals['ui'].add_text_to_column2(f'\tnode {self.node_id} got config from node {message.sending_id}')

            config = NodeConfig(**json.loads(message.message))
            self.ledger[message.sending_id] = config

            if message.channel == 0x02:
                self.send_message(message.sending_id, str(self.config), 0x00)

            else:
                if message.receiving_id == self.node_id:
                    self.change_config('measurement_interval', str(config.measurement_interval))
                    self.change_config('requested_replications', str(config.requested_replications))
        elif message.channel == 0x03:
            """ handle replication bidding messages """
            globals['ui'].add_text_to_column2(f'\tnode {self.node_id} got replication bid from node {message.sending_id}')

            if self.replication_bidding_timer is None or not self.replication_bidding_timer.is_alive():
                globals['ui'].add_text_to_column2(f'\tnode {self.node_id} starting replication bidding timer')
                self.replication_bidding_timer = Timer(1, self.handle_replication_bidding)
                self.replication_bidding_timer.start()
            else:
                globals['ui'].add_text_to_column2(f'\tnode {self.node_id} already has a replication bidding timer running')

            # add the bid to the list of bids
            self.replication_bids[message.sending_id] = int(message.message)

        else :
            globals['ui'].add_text_to_column2(f'\tnode {self.node_id} got unknown message from node {message.sending_id} on channel {message.channel}')

    def handle_replication_bidding(self):
        globals['ui'].add_text_to_column2(f'\tnode {self.node_id} handling replication bidding')
        # check how many winners there will be
        winner_count = self.config.requested_replications - len(self.config.replicating_nodes)

        # get n random unique nodes that have bid
        nodes = list(self.replication_bids.keys())
        random_nodes = []
        for i in range(winner_count):
            random_nodes.append(nodes.pop(math.floor(random() * len(nodes))))

        # update the config and send it to the network
        self.config.replicating_nodes = [ReplicationInfo(i, 1) for i in random_nodes]
        self.send_message(0xFF, str(self.config), 0x00)

    def start_measurements(self):
        self.repeated_timer.start()

    def stop_measurements(self):
        self.repeated_timer.stop()

    def change_config(self, key: str, value: str):
        if key == 'measurement_interval':
            self.repeated_timer.stop()
            self.repeated_timer = RepeatedTimer(float(value), self.measure)
            self.repeated_timer.start()
            self.config.measurement_interval = float(value)

        if key == 'requested_replications':
            self.config.requested_replications = int(value)
        else:
            print('unknown config key: ', key)
            return

        globals['ui'].add_text_to_column1(f'node {self.node_id} changed config: {key} to {value}', False)
