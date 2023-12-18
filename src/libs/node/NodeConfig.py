import pickle

from libs.helpers.dict import diff_dict

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
        return deepcopy(self)

    def serialize(self):
        return pickle.dumps(self)

    @staticmethod
    def deserialize(data: any):
        if isinstance(data, str):
            obj = json.loads(data)
            return NodeConfig(
                requested_replications=obj['requested_replications'],
                measurement_interval=obj['measurement_interval'],
                replicating_nodes=obj['replicating_nodes'],
                replication_timeout=obj['replication_timeout']
            )
        elif isinstance(data, bytes):
            return pickle.loads(data)

    def diff_config(self, new_config):
        """ diff the config with the new config using the diff_dict. function"""
        # a diff will consist of a set with the following type (int, any)
        # the int will be the change. 1 if added, 0 if removed, 2 if changed

        diff = {}

        # if they are both the same we will return an empty diff
        # we will skip the diffing step as nothing needs to change
        if self == new_config:
            return diff

        return diff_dict(self.__dict__, new_config.__dict__)

    def apply_diff(self, diff):
        """ apply the diff to the config. """
        for key, value in diff:
            if key == 'measurement_interval':
                self.measurement_interval = float(value)

            if key == 'requested_replications':
                self.requested_replications = int(value)

            if key == 'replicating_nodes':
                self.replicating_nodes = value

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
