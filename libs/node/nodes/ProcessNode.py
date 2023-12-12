from libs.node.nodes.controllers.ReplicationController import ReplicationController
from libs.node.nodes.controllers.StorageController import StorageController
from libs.node.nodes.controllers.ConfigController import ConfigController
from libs.node.nodes.actions.RepeatMeasurement import RepeatMeasurement
from libs.node.nodes.abstracts.BaseNode import BaseNode
from libs.node.ReplicationInfo import ReplicationInfo
from libs.RepeatedTimer import RepeatedTimer
from libs.network.Channel import ChannelID
from libs.node.NodeConfig import NodeConfig
from libs.network.Message import Message

import threading
import pickle
import socket
import time


class ProcessNode(BaseNode):
    """ node that runs in a separate process.
        this is a combination of the randomNode and the SocketClient example."""

    replication_controller: ReplicationController
    storage_controller: StorageController
    config_controller: ConfigController
    repeated_timer: RepeatedTimer

    socket: socket.socket

    def __init__(self, network: tuple[str, int], node_id, config, x, y, r):
        super().__init__(node_id, x, y, r)
        # network node info
        self.received_messages = []
        self.messages_send_counter = 0

        # set up and connect the socket
        self.socket = self.connect(network[0], network[1])

        # start listening to incoming messages
        self.listen_thread = threading.Thread(target=self.listen)
        self.listen_thread.daemon = True
        self.listen_thread.start()

        # set up rest of the node
        # setup controllers
        self.config_controller = ConfigController(
            node_id,
            config,
            lambda message: self.send_message(0xFF, message, ChannelID.CONFIG.value)
        )



        self.replication_controller = ReplicationController(
            self.config_controller['replication_timeout'],
            self.config_controller['requested_replications'],
            lambda: self.config_controller.get_current_replicators(self.node_id),
            lambda winners: self.config_controller.change_config('replicating_nodes', winners)
        )

        self.storage_controller = StorageController(node_id)

        # create the repeated measurement
        self.repeated_measurement = RepeatMeasurement(
            self.config_controller['measurement_interval'],
            [
                lambda m: self.storage_controller(m, self.node_id),  # store measurement locally
                lambda m: self.send_message(0xFF, m.serialize(), 0x01)  # send measurement to network
            ]
        )

        # start the node
        self.repeated_measurement.start()  # start making measurements
        self.send_message(0xFF, self.config.serialize(), ChannelID.DISCOVERY.value)  # broadcast config

    def connect(self, host, port):
        """ connect to a socket and send the node info """
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        info = {
            'node_id': self.node_id,
            'x': self.x,
            'y': self.y,
            'r': self.r
        }

        s.sendall(pickle.dumps(info))
        return s

    def disconnect(self):
        """ disconnect from the socket """
        self.socket.close()

    def listen(self):
        """ listen for messages """

        while True:
            data = self.socket.recv(2048)
            if not data:
                return

            print(data)
            msg = pickle.loads(data)

            self.rec_message(msg)
            self.received_messages.append(msg.msg_id)

    def send_message(self, receiving_id: int, payload, channel):
        """ send a message to the network """
        nid_bytes = self.node_id.to_bytes(2, 'big')
        counter_bytes = self.messages_send_counter.to_bytes(6, 'big')
        msg_id = b'|'.join([nid_bytes, counter_bytes])

        msg = Message(
            receiving_id=receiving_id,
            sending_id=self.node_id,
            channel=channel,
            payload=payload,
            msg_id=msg_id
        )

        msg_bytes = pickle.dumps(msg)
        # send message
        self.socket.sendall(msg_bytes)

        self.messages_send_counter += 1
        time.sleep(0.01)

    def send_bytes(self, bytes: bytes):
        """ send bytes to the network """
        self.socket.sendall(bytes)

    def rec_message(self, message):
        # check if we send it or have recieved it earlier
        if message.sending_id == self.node_id or message.msg_id in self.received_messages:
            return

        # propagate the message if it is not only for this node
        if message.receiving_id != self.node_id:
            self.propagate_message(message)

        if message.receiving_id == self.node_id or message.receiving_id == 0xFF:
            self.handle_message(message)

    def handle_message(self, message: Message):
        print(
            f'node {self.node_id} received message from {message.sending_id} on channel {message.channel} with payload {message.payload}')

        if message.channel == ChannelID.CONFIG.value:
            self.config_controller.handle_message(message)
        elif message.channel == ChannelID.MEASUREMENT.value:
            self.handle_measurement_message(message)
        elif message.channel == ChannelID.DISCOVERY.value:
            self.handle_discovery_message(message)
        elif message.channel == ChannelID.REPLICATION_BIDDING.value:
            if message.receiving_id != self.node_id or \
                    len(self.config_controller['replicating_nodes']) >= self.config.requested_replications:
                return

            self.replication_controller.add_bid(message.sending_id, int(message.payload))

    def propagate_message(self, message: Message):
        # TODO:: implement better routing algorithm
        message.hops += 1
        self.send_message(message.receiving_id, message.payload, message.channel)

    def handle_measurement_message(self, message):
        # find the nodes config in ledger
        if message.sending_id not in self.config_controller.ledger:
            # if the node isn't in the ledger we will send a discovery message to the node.
            # this will prompt the node to send its config onto the network.
            # this message doesn't contain a message as it is not needed

            # check how many nodes where replicating
            return self.send_message(message.sending_id, '', ChannelID.DISCOVERY.value)

        # get the node that send the message config
        cnf = self.config_controller.get_nodes_config(message.sending_id)

        # at this point we know who the node is and we have its config
        if self.node_id in cnf.replicating_nodes:
            # if we will parse and store the measurement
            m = Measurement.deserialize(message.payload)
            self.storage_controller(m, message.sending_id)

        else:
            # if we aren't in the ledger we will check if it has enough replicating nodes
            # if it hasn't we will send a replication bidding message
            if self.node_id == message.sending_id:
                return

            if len(cnf.replicating_nodes) < cnf.requested_replications:
                # send replication bidding message
                self.send_message(message.sending_id, str(message.hops), ChannelID.REPLICATION_BIDDING.value)

    def handle_discovery_message(self, message):
        self.send_message(message.sending_id, str(self.config), ChannelID.CONFIG.value)


    def change_config(self, key: str, value):
        """ Change the config of the node. """
        # depending on which value needs to be changed we will convert the value to a different type

        # TODO:: Fix this
        # if key == 'measurement_interval':
        #     self..change_interval(float(value))
        #     self.config.measurement_interval = float(value)

        self.send_config_update()

    def send_config_update(self):
        self.send_message(0xFF, str(self.config), ChannelID.CONFIG.value)

    @property
    def config(self):
        return self.config_controller.config


if __name__ == '__main__':
    node_id = 0x84

    cnf = NodeConfig(5, 2, [ReplicationInfo(node_id, 0)])
    node = ProcessNode(
        ('localhost', 8080),
        node_id,
        NodeConfig(
            5,
            2,
            [ReplicationInfo(node_id, 0)]
        ),
        0,
        0,
        5
    )

    while True:
        time.sleep(1)
