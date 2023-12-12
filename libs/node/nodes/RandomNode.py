from libs.node.ReplicationInfo import ReplicationInfo
from libs.node.nodes.NetworkNode import NetworkNode
from libs.network.Measurement import Measurement
from libs.RepeatedTimer import RepeatedTimer
from libs.node.NodeConfig import NodeConfig
from libs.network.Channel import ChannelID
from libs.network.Message import Message
from libs.network.networks.Network import Network

from datetime import datetime, timezone
from tinyflux import TinyFlux, Point
from threading import Timer
from globals import globals
from random import random, randint

import math
import json
import os

from libs.node.nodes.actions.RepeatMeasurement import RepeatMeasurement, StoreData


class RandomNode(NetworkNode):
    """ This is a node that sends random measurements to the network.
        The rate of measurements can be adjusted by updating the config. """
    repeated_timer: RepeatedTimer

    ledger: dict[int, NodeConfig]
    replication_bids: dict[int, int]

    def __init__(self, network: Network, node_id: int, config: NodeConfig, x: int, y: int, r: int):
        super().__init__(network, node_id, x, y, r)

        self.ledger = {}

        self.replication_bidding_timer = None
        self.replication_bids = {}

        self.config = config

        # send discovery message
        self.send_message(0xFF, str(self.config), 0x02)

        # generate a random file path. this is where the database will be stored.
        # the database used for testing will make use of a csv file for easy reading.
        self.path = f'./tmp/databases/{datetime.now(timezone.utc).timestamp()}_{math.floor(random() * 92121)}_{node_id}.csv'
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        self.db = TinyFlux(self.path)

        # start making measurements periodically.
        # also store the measurements locally and send them to the network
        self.repeated_measurement = RepeatMeasurement(
            self.config.measurement_interval,
            [
                StoreData(self.db, self.node_id),  # store measurement locally
                lambda m: self.send_message(0xFF, str(m), 0x01)  # send measurement to network
            ]
        )

        self.repeated_measurement.start()

    def handle_message(self, message: Message):
        """ handle messages that get send to this node.
            This function will only receive messages that are for this node. """
        if self.node_id == message.sending_id:
            return

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

        # if we are already replicating this node we will ignore the bid
        if message.sending_id in [i.node_id for i in self.config.replicating_nodes]:
            return

        # if there is no timer running we will start one
        if self.replication_bidding_timer is None or not self.replication_bidding_timer.is_alive():
            self.replication_bidding_timer = Timer(1, self.decide_replication_winner)
            self.replication_bidding_timer.start()

        # add the bid to the list of bids
        self.replication_bids[message.sending_id] = int(message.payload)

        # globals['logger'].print(f'{self.node_id}, {self.replication_bids}')

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

            # check how many nodes where replicating
            return self.send_message(message.sending_id, '', ChannelID.DISCOVERY.value)

        # TODO:: investigate why this is a dict
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
            if self.node_id == message.sending_id:
                return

            cnf = self.ledger[message.sending_id]
            if len(cnf.replicating_nodes) < cnf.requested_replications:
                # send replication bidding message
                self.send_message(message.sending_id, str(message.hops), ChannelID.REPLICATION_BIDDING.value)

    def decide_replication_winner(self):
        """ Decide the winners of the replication bidding and update the config to reflect this. """
        # check how many winners there will be
        winner_count = self.config.requested_replications - len(self.config.replicating_nodes)

        # get n random unique nodes that have bid
        nodes = list(self.replication_bids.keys())
        if len(nodes) == 0:
            globals['ui'].add_text_to_column2('no nodes have bid')
            return

        # the current algorithm will sort the nodes by the amount of hops. next it will split the list into n segments
        # where n is the amount of winners we need. then it will pick a random node from each segment. this will
        # ensure that we have nodes that are at least a different amount of hops away from us.
        # TODO:: implement better algorithm to choose winners.
        sorted_bids = sorted(self.replication_bids.items(), key=lambda x: x[1])

        segment_size = len(sorted_bids) // winner_count
        if segment_size == 0:
            # take all bids
            segment_size = 1

        for i in range(min(winner_count, math.ceil(len(sorted_bids) / segment_size))):
            index = randint(i * segment_size, (i + 1) * segment_size - 1)

            node = sorted_bids[index][0]
            if node not in self.config.replicating_nodes:
                # append the node and the amount of hops it is away from the node that send the measurement
                self.config.replicating_nodes.append(ReplicationInfo(node, sorted_bids[index][1]))

        # clear the list of bids
        self.replication_bids = {}
        self.send_config_update()

    def send_config_update(self):
        """ send the config to the network"""
        self.send_message(0xFF, str(self.config), ChannelID.CONFIG.value)

    def shutdown(self):
        """ Stop sending measurements to the network. """
        self.repeated_measurement.stop()

    def change_config(self, key: str, value: str):
        """ Change the config of the node. """
        # depending on which value needs to be changed we will convert the value to a different type
        if key == 'measurement_interval':
            self.repeated_measurement.change_interval(float(value))
            self.config.measurement_interval = float(value)

        if key == 'requested_replications':
            self.config.requested_replications = int(value)
