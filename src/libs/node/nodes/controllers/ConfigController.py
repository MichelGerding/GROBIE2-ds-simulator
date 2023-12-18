import json

from libs.helpers.dict import serialize_dict
from libs.network.Channel import ChannelID
from libs.node.NodeConfig import NodeConfig
from libs.network.Message import Message

from typing import Callable

class ConfigController:
    """ This class is used to handle the config of the node.
        this includes sending the config to the network and receiving the config from the network.
        this logic is moved into a seperate class to make it easier to change"""

    # TODO:: make use of diffing the config. this will reduce the size of the messages

    config: NodeConfig
    ledger: dict[int, NodeConfig]

    def __init__(self, node_id: int, config: NodeConfig, send_message: Callable[[str], None]):
        self.config = config
        self.ledger = {
            node_id: config
        }

        self.send_message = send_message

    def handle_message(self, message: Message, own_config: bool = False) -> None:
        if message.channel == ChannelID.CONFIG.value:
            config = NodeConfig.deserialize(message.payload)

            self.modify_ledger(message.sending_id, config)

            if own_config:
                self.change_config('measurement_interval', str(config.measurement_interval), False)
                self.change_config('requested_replications', str(config.requested_replications))

    def modify_ledger(self, node_id: int, config: NodeConfig) -> None:
        """ Modify the ledger of the node. """
        self.ledger[node_id] = config

    def remove_from_ledger(self, node_id: int) -> None:
        """ Remove a node from the ledger. """
        del self.ledger[node_id]

    def change_config(self, key: str, value, update=True) -> None:
        """ Change the config of the node. """
        # depending on which value needs to be changed we will convert the value to a different type

        # TODO:: allow modification to the measurement interval

        if key == 'requested_replications':
            self.config.requested_replications = int(value)

        if key == 'replicating_nodes':
            self.config.replicating_nodes = value

        if update:
            self.send_config_update(self.config)

    def send_config_update(self, new_config: NodeConfig, full_config=True) -> None:
        """ send the config to the network
        """
        if full_config:
            return self.send_message(new_config.serialize())

        diff = self.config.diff_config(new_config)
        self.send_message(serialize_dict(diff))

    def get_nodes_config(self, node_id: int) -> NodeConfig:
        return self.ledger[node_id]

    def get_current_replicators(self, node_id) -> dict[int, int]:
        return self.ledger[node_id].replicating_nodes

    # inde the config of the node using []
    def __getitem__(self, key):
        return getattr(self.config, key)
