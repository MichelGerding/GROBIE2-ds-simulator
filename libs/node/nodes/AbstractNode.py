from libs.network.Network import Network, Message
from libs.node.NodeConfig import NodeConfig

from abc import abstractmethod, ABC

import json


class AbstractNode(ABC):
    """ Abstract node. all nodes should extend this class.
        This class is responsible for filtering messages and sending messages to the network. """
    node_id: int
    network: Network

    def __init__(self, network: Network, node_id: int, config: NodeConfig):
        """ Initialize the node. """
        self.network = network
        self.node_id = node_id
        self.config = config

        network.subscribe_to_messages(self)

    def on_message(self, message: Message):
        """ Receive incoming messages.
            all this function will do is check if we should handle the
            message and if so pass it to the inheriting class. """
        # if the message is for me or broadcast to all nodes we will handle it.
        # except if it im the sender.

        # make sure we don't handle messages that we send, or we might end up in a loop
        if message.sending_id == self.node_id:
            return

        # if the message is for us or broadcast to all nodes we will handle it.
        if message.receiving_id == self.node_id or message.receiving_id == 0xFF:
            self.handle_message(message)

        # any other case we will ignore the message

    def __str__(self):
        """ return a json string of the node """
        return json.dumps({
            'node_id': self.node_id,
            'config': {
                'measurement_interval': self.config.measurement_interval,
                'requested_replications': self.config.requested_replications,
                'replicating_nodes': [{hex(i.node_id): i.hops} for i in self.config.replicating_nodes]

            }
        }, sort_keys=True)

    @abstractmethod
    def handle_message(self, message: Message):
        """ Handle incoming messages. """
        raise NotImplementedError("Method is abstract and not implemented")

    def send_message(self, receiving_id: int, msg: str, channel: int):
        """ Send a message to the network """
        self.network.send_message(Message(
            message=msg,
            sending_id=self.node_id,
            receiving_id=receiving_id,
            channel=channel
        ))
