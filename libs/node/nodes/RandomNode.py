import json
import pickle

from libs.node.nodes.controllers.ReplicationController import ReplicationController
from libs.node.nodes.controllers.StorageController import StorageController
from libs.node.nodes.controllers.ConfigController import ConfigController
from libs.node.nodes.actions.RepeatMeasurement import RepeatMeasurement
from libs.node.nodes.abstracts.NetworkNode import NetworkNode
from libs.network.networks.Network import Network
from libs.network.Measurement import Measurement
from libs.RepeatedTimer import RepeatedTimer
from libs.node.NodeConfig import NodeConfig
from libs.network.Channel import ChannelID
from libs.network.Message import Message


class RandomNode(NetworkNode):
    """ This is a node that sends random measurements to the network.
        The rate of measurements can be adjusted by updating the config. """

    replication_bidding_controller: ReplicationController
    storage_controller: StorageController
    config_controller: ConfigController
    repeated_timer: RepeatedTimer

    def __init__(self, network: Network, node_id: int, config: NodeConfig, x: int, y: int, r: int):
        super().__init__(network, node_id, x, y, r)

        # create the controllers. the controllers will handle generic logic like replications, configuration,
        # storage, ...
        # this is done so that it is easier to change the logic but also add new types of nodes as the logic is
        # seperated from the node itself.
        self.config_controller = ConfigController(
            node_id,
            config,
            lambda message: self.send_message(0xFF, message, ChannelID.CONFIG.value)
        )

        self.replication_bidding_controller = ReplicationController(
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

    def handle_message(self, message: Message):
        """ handle messages that get send to this node.
            This function will only receive messages that are for this node. """
        if self.node_id == message.sending_id:
            return

        # call the function that handles messages for the channel
        if hasattr(self, 'handle_' + ChannelID(message.channel).name.lower() + '_message'):
            getattr(self, 'handle_' + ChannelID(message.channel).name.lower() + '_message')(message)
        else:
            print(f'No handler for channel {ChannelID(message.channel).name.lower()}')

    def handle_client_message(self, message: Message):
        """ handle messages that are send by the user. """
        # parse the clients message. this will have the following format
        # {"cmd", "node_id", "daterange?": {"start", "end"}}
        print(f'handling client message {message.payload}')

        query_info = json.loads(message.payload)
        node_id = query_info['node_id']

        # get the data from the database
        data = self.storage_controller.get_data(node_id)
        bits = pickle.dumps(data)
        # send the message on the client network
        self.send_message(message.sending_id, bits, ChannelID.CLIENT.value)

    def handle_replication_bidding_message(self, message: Message):
        if message.receiving_id != self.node_id or \
                len(self.config_controller['replicating_nodes']) >= self.config.requested_replications:
            return

        self.replication_bidding_controller.add_bid(message.sending_id, int(message.payload))

    def handle_config_message(self, message: Message):
        """ handle config messages. these messages contain the config of a node. """
        self.config_controller.handle_message(message)

    def handle_discovery_message(self, message: Message):
        """ if we get a discovery request we will broadcast our config. we will broadcast instead of uni-cast so
            that all nodes can update their ledger as one or more nodes don't have our config"""
        self.send_message(message.sending_id, self.config.serialize(), ChannelID.CONFIG.value)

    def handle_measurement_message(self, message: Message):
        """ handle messages that contain measurements we will only store the measurements if we know the node that
            send it, and they want us to replicate if the node doesn't want us to replicate we will check if he has
            enough replicating nodes if he doesn't we will send a replication bidding message. this contains with
            the amount of hops we are away from the node that send the measurement. The measurement will be
            discarded but if we win we will store the next measurements we get from the node. """

        # find the nodes config in ledger
        if message.sending_id not in self.ledger.keys():
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
                self.send_message(message.sending_id, str(message.ttl), ChannelID.REPLICATION_BIDDING.value)

    def shutdown(self):
        """ Stop sending measurements to the network. """
        self.repeated_measurement.stop()
        self.send_message(0xFF, '', ChannelID.DISCONNECT.value)

    def change_config(self, key: str, value):
        """ Change the config of the node. """
        self.config_controller.change_config(key, value)

    @property
    def config(self):
        return self.config_controller.config

    @property
    def ledger(self):
        return self.config_controller.ledger
