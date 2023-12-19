import pickle

from libs.helpers.dict import diff_dict, apply_diff

from dataclasses import dataclass
from copy import deepcopy

import json


@dataclass
class NodeConfig:
    """ configuration for a node.
        This is used to configure a node

        requested_replications: int # the amount of nodes that should replicate this node
        measurement_interval: float # the interval in seconds in which the node should send a message
        replicating_nodes: list[ReplicationInfo] currently the nodes that this node is replicating.
                                                 will be changed to nodes that are replicating this node
        """
    requested_replications: int
    measurement_interval: float
    replicating_nodes: dict[int, int]
    max_replications: int = 4
    replication_timeout: float = 0.1

    def __str__(self):
        return json.dumps({
            'requested_replications': self.requested_replications,
            'measurement_interval': self.measurement_interval,
            'replicating_nodes': self.replicating_nodes,
            'replication_timeout': self.replication_timeout,
        }, sort_keys=True)

    def copy(self):
        cp = NodeConfig(0, 0, {})
        cp.requested_replications = deepcopy(self.requested_replications)
        cp.measurement_interval = deepcopy(self.measurement_interval)
        cp.replicating_nodes = deepcopy(self.replicating_nodes)  # Create a new instance of replicating_nodes
        cp.max_replications = deepcopy(self.max_replications)
        cp.replication_timeout = deepcopy(self.replication_timeout)
        return cp

    def serialize(self):
        return pickle.dumps(self)

    @staticmethod
    def deserialize(data: any):
        return pickle.loads(data)

    def diff_config(self, new_config):
        """ diff the config with the new config using the diff_dict. function"""
        # if they are both the same we will return an empty diff
        # we will skip the diffing step as nothing needs to change
        if self == new_config:
            return {}

        diff = diff_dict(self.__dict__, new_config.__dict__)

        print(json.dumps({
            'diff': diff,
            'old': self.__dict__,
            'new': new_config.__dict__
        }, indent=4, sort_keys=True))
        return diff


    def apply_diff(self, diff: dict):
        """ apply the diff to the config. """
        new_config = apply_diff(self.__dict__, diff)
        self.requested_replications = new_config['requested_replications']
        self.measurement_interval = new_config['measurement_interval']
        self.replicating_nodes = new_config['replicating_nodes']
        self.max_replications = new_config['max_replications']
        self.replication_timeout = new_config['replication_timeout']


    def __eq__(self, other):
        return self.__dict__ == other.__dict__
