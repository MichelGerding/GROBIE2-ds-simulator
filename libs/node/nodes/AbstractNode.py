from abc import abstractmethod, ABC

from libs.node.NodeConfig import NodeConfig
from libs.network.Network import *

import json


class AbstractNode(ABC):
    node_id: int
    channel: int
    network: Network

    def __init__(self, network: Network, node_id: int, channel: int, config: NodeConfig):
        self.network = network
        self.node_id = node_id
        self.channel = channel
        self.config = config

        network.subscribe_to_messages(self)

    def on_message(self, message: Message):
        # if the message is for me or broadcast to all nodes we will handle it.
        # except if it im the sender.
        if (message.receiving_id == self.node_id or message.receiving_id == 0xFF) and message.sending_id != self.node_id:
            self.handle_message(message)

    def __str__(self):
        return json.dumps({
            'node_id': self.node_id,
            'channel': self.channel,
            'config': {
                'measurement_interval': self.config.measurement_interval,
                'requested_replications': self.config.requested_replications,
                'replicating_nodes': [{hex(i.node_id): i.hops} for i in self.config.replicating_nodes]

            }
        }, sort_keys=True)

    @abstractmethod
    def handle_message(self, message: Message):
        raise NotImplementedError("Method is abstract and not implemented")

    def send_message(self, receiving_id: int, msg: str, channel: int):
        self.network.send_message(Message(
            message=msg,
            sending_id=self.node_id,
            receiving_id=receiving_id,
            channel=channel
        ))
