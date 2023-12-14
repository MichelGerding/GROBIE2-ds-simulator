from libs.node.NodeConfig import NodeConfig
from libs.network.Message import Message

from typing import Callable

import json

from libs.node.ReplicationInfo import ReplicationInfo


class ConfigController:
    """ This class is used to handle the config of the node.
        this includes sending the config to the network and receiving the config from the network.
        this logic is moved into a seperate class to make it easier to change"""

    # TODO:: implement diffing of config to only send the changed values
    # TODO:: send messages as bytes. this will reduce the size of the messages

    config: NodeConfig
    ledger: dict[int, NodeConfig]

    def __init__(self, node_id: int, config: NodeConfig, send_message: Callable[[str], None]):
        self.config = config
        self.ledger = {
            node_id: config
        }

        self.send_message = send_message

    def handle_message(self, message: Message, own_config: bool = False):
        json_parsed = json.loads(message.payload)
        config = NodeConfig(
            measurement_interval=json_parsed['measurement_interval'],
            requested_replications=json_parsed['requested_replications'],
            replicating_nodes=[ReplicationInfo(int(x['node_id'], 16), x['hops']) for x in json_parsed['replicating_nodes']]
        )

        self.ledger[message.sending_id] = config

        if own_config:
            self.change_config('measurement_interval', str(config.measurement_interval))
            self.change_config('requested_replications', str(config.requested_replications))

    def modify_ledger(self, node_id: int, config: NodeConfig):
        """ Modify the ledger of the node. """
        self.ledger[node_id] = config

    def remove_from_ledger(self, node_id: int):
        """ Remove a node from the ledger. """
        del self.ledger[node_id]

    def change_config(self, key: str, value):
        """ Change the config of the node. """
        # depending on which value needs to be changed we will convert the value to a different type

        # TODO:: Fix this
        # if key == 'measurement_interval':
        #     self..change_interval(float(value))
        #     self.config.measurement_interval = float(value)

        if key == 'requested_replications':
            self.config.requested_replications = int(value)

        if key == 'replicating_nodes':
            self.config.replicating_nodes = value

        self.send_config_update(self.config)

    def send_config_update(self, new_config: NodeConfig):
        """ send the config to the network"""
        self.send_message(str(new_config))

    def get_nodes_config(self, node_id: int):
        return self.ledger[node_id]

    def get_current_replicators(self, node_id):
        return self.ledger[node_id].replicating_nodes

    # indes the config of the node using []
    def __getitem__(self, key):
        return getattr(self.config, key)
