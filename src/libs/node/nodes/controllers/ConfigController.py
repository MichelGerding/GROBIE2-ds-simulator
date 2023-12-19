import json
import pickle

from libs.helpers.dict import serialize_dict, diff_dict
from libs.network.Channel import ChannelID
from libs.node.NodeConfig import NodeConfig
from libs.network.Message import Message

from typing import Callable

from copy import deepcopy


class ConfigController:
    """ This class is used to handle the config of the node.
        this includes sending the config to the network and receiving the config from the network.
        this logic is moved into a seperate class to make it easier to change"""

    # TODO:: increase use of config diffing
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
            config = pickle.loads(message.payload)

            self.modify_ledger(message.sending_id, config)

            if isinstance(config, NodeConfig) and own_config:
                self.change_config({
                    'requested_replications': config.requested_replications,
                    'measurement_interval': config.measurement_interval
                })

    def modify_ledger(self, node_id: int, config: NodeConfig | dict) -> None:
        """ Modify the ledger of the node. """

        if isinstance(config, dict):
            if node_id in self.ledger:
                self.ledger[node_id].apply_diff(config)
        else:
            self.ledger[node_id] = config

    def remove_from_ledger(self, node_id: int) -> None:
        """ Remove a node from the ledger. """
        del self.ledger[node_id]

    def change_config(self, new: any, update=True, key=None):
        # FIXME:: allow modification to the measurement interval

        # TODO:: lower amount of deepcopies needed
        cnf = self.config.copy()
        print(f'before changes: {cnf}')

        changes = False

        if key is not None:
            if key != 'measurement_interval':
                if getattr(cnf, key) == new:
                    print('no change needed')
                else:
                    changes = True
                    setattr(cnf, key, deepcopy(new))
        else:
            for key, val in new.items():
                if getattr(cnf, key) == val:
                    print('no change needed')
                    continue

                if key != 'measurement_interval':
                    changes = True
                    setattr(cnf, key, deepcopy(val))

        print(f'after changes: {cnf}')

        if update and changes:
            diff = self.send_config_update(cnf, False)
            self.config.apply_diff(diff)

    def send_config_update(self, new_config: NodeConfig, full_config=True) -> None | dict:
        """ send the config to the network
        """
        if full_config:
            return self.send_message(new_config.serialize())

        diff = self.config.diff_config(new_config)
        self.send_message(serialize_dict(diff))
        return diff

    def get_nodes_config(self, node_id: int) -> NodeConfig:
        return self.ledger[node_id]

    def get_current_replicators(self, node_id) -> dict[int, int]:
        return deepcopy(self.ledger[node_id].replicating_nodes)

    # index the config of the node using []
    def __getitem__(self, key):
        return getattr(self.config, key)
