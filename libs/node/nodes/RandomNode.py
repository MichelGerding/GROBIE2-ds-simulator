from libs.node.ReplicationInfo import ReplicationInfo
from libs.node.nodes.NetworkNode import NetworkNode
from libs.network.Measurement import Measurement
from libs.RepeatedTimer import RepeatedTimer
from libs.node.NodeConfig import NodeConfig
from libs.network.Channel import ChannelID
from libs.network.Message import Message
from libs.network.Network import Network

from datetime import datetime, timezone
from tinyflux import TinyFlux, Point
from threading import Timer
from globals import globals
from random import random

import math
import json
import os


class RandomNode(NetworkNode):
    """ This is a node that sends random measurements to the network.
        The rate of measurements can be adjusted by updating the config. """
    repeated_timer: RepeatedTimer

    ledger: dict[int, NodeConfig] = {}
    replication_bids: dict[int, int] = {}

    def __init__(self, network: Network, node_id: int, config: NodeConfig, x: int, y: int, r: int):
        super().__init__(network, node_id, config, x, y, r)
        self.replication_bidding_timer = None
        self.repeated_timer = RepeatedTimer(config.measurement_interval, self.measure)
        self.config = config

        # send discovery message
        self.send_message(0xFF, str(self.config), 0x02)

        # generate a random file path. this is where the database will be stored.
        # the database used for testing will make use of a csv file for easy reading.
        # the database used for the final product will use a sqlite database.
        self.path = f'./tmp/databases/{datetime.now(timezone.utc).timestamp()}_{math.floor(random() * 92121)}_{node_id}.csv'

        # make sure the directory exists
        os.makedirs(os.path.dirname(self.path), exist_ok=True)

        # TODO:: change to sqlite for improved capacity
        self.db = TinyFlux(self.path)

    def measure(self):
        """ measure the temperature and light and send it to the network.
            This function will also store the measurement in the database. """
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

        if message.channel == ChannelID.CONFIG.value:
            self.handle_config_message(message)
        elif message.channel == ChannelID.MEASUREMENT.value:
            self.handle_measurement_message(message)
        elif message.channel == ChannelID.DISCOVERY.value:
            self.handle_discovery_message(message)
        elif message.channel == ChannelID.REPLICATION_BIDDING.value:
            self.handle_replication_bid_message(message)

    def handle_discovery_message(self, message: Message):
        """ if we get a discovery request we will broadcast our config. we will broadcast instead of uni-cast so
            that all nodes can update their ledger as one or more nodes don't have our config"""
        self.send_message(message.sending_id, str(self.config), 0x00)

    def handle_config_message(self, message: Message):
        """ if we get a message on the config channel we will update the ledger with this config.
            if the message is for us, we will also update our config """

        config = NodeConfig(**json.loads(message.payload))
        self.ledger[message.sending_id] = config

        if message.receiving_id == self.node_id:
            self.change_config('measurement_interval', str(config.measurement_interval))
            self.change_config('requested_replications', str(config.requested_replications))

    def handle_replication_bid_message(self, message: Message):
        """ to add new replications we will use a bidding system. the node that wants to replicate will send a bid
            being the amount of hops he is from the node that send the measurement. the node that send the measurement
            will then pick n random nodes that have bid and send them a message that they should replicate the node.
            after this the config of the node that send the measurement will be updated so all nodes know which nodes
            are replicating """

        # if the bid is not for us we will ignore it
        if message.receiving_id != self.node_id:
            return
        # if there is no timer running we will start one
        if self.replication_bidding_timer is None or not self.replication_bidding_timer.is_alive():
            self.replication_bidding_timer = Timer(1, self.handle_replication_bidding)
            self.replication_bidding_timer.start()

        # add the bid to the list of bids
        self.replication_bids[message.sending_id] = int(message.payload)

        globals['logger'].print(f'{self.node_id}, {self.replication_bids}')

    def handle_measurement_message(self, message: Message):
        """ handle messages that contain measurements we will only store the measurements if we know the node that
            send it, and they want us to replicate if the node doesn't want us to replicate we will check if he has
            enough replicating nodes if he doesn't we will send a replication bidding message. this contains with
            the amount of hops we are away from the node that send the measurement. The measurement will be
            discarded but if we win we will store the next measurements we get from the node. """

        # find the nodes config in ledger
        if message.sending_id not in self.ledger:
            # if the node isn't in the ledger we will send a discovery message to the node.
            # this will prompt the node to send its config onto the network.
            # this message doesn't contain a message as it is not needed
            return self.send_message(message.sending_id, '', ChannelID.DISCOVERY.value)

        # at this point we know who the node is and we have its config
        if self.node_id in [int(i['node_id'], 16) for i in self.ledger[message.sending_id].replicating_nodes]:
            # if we are already replicating this node we will store the measurement
            m = Measurement(**json.loads(message.payload))
            self.db.insert(Point(
                time=datetime.now(timezone.utc),
                tags={"node": hex(message.sending_id)},
                fields={"temp": m.temp, "light": m.light}
            ))

        else:
            # if we aren't in the ledger we will check if it has enough replicating nodes
            # if it hasn't we will send a replication bidding message

            cnf = self.ledger[message.sending_id]
            if len(cnf.replicating_nodes) < cnf.requested_replications:
                # send replication bidding message
                self.send_message(message.sending_id, str("1"), ChannelID.REPLICATION_BIDDING.value)

    def handle_replication_bidding(self):
        """ Decide the winners of the replication bidding and update the config to reflect this. """
        # check how many winners there will be
        winner_count = self.config.requested_replications - len(self.config.replicating_nodes)

        # get n random unique nodes that have bid
        nodes = list(self.replication_bids.keys())
        if len(nodes) == 0:
            globals['ui'].add_text_to_column2('no nodes have bid')
            return

        random_nodes = []
        for i in range(winner_count):
            if len(nodes) == 0:
                break

            random_nodes.append(nodes.pop(math.floor(random() * len(nodes))))

        # update the config and send it to the network
        self.config.replicating_nodes = [ReplicationInfo(i, 1) for i in random_nodes]
        self.send_message(0xFF, str(self.config), ChannelID.CONFIG.value)

    def start_measurements(self):
        """ Start sending measurements to the network. """
        self.repeated_timer.start()

    def stop_measurements(self):
        """ Stop sending measurements to the network. """
        self.repeated_timer.stop()

    def change_config(self, key: str, value: str):
        """ Change the config of the node. """
        # depending on which value needs to be changed we will convert the value to a different type
        if key == 'measurement_interval':
            # if we want to change the interval of the measurements we will need to create a new
            # RepeatedTimer as we can't adjust the interval of the current one
            self.repeated_timer.stop()
            self.repeated_timer = RepeatedTimer(float(value), self.measure)
            self.repeated_timer.start()
            self.config.measurement_interval = float(value)

        if key == 'requested_replications':
            self.config.requested_replications = int(value)
