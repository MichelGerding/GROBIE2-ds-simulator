from dataclasses import dataclass

import json

@dataclass
class ReplicationInfo:
    node_id: int
    hops: int

    def __str__(self):
        return json.dumps({
            'node_id': self.node_id,
            'hops': self.hops
        }, sort_keys=True)

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
    replicating_nodes: list[ReplicationInfo]

    def __str__(self):

        replicating_nodes_json = []
        for r in self.replicating_nodes:
            replicating_nodes_json.append({hex(r.node_id): r.hops})

        return json.dumps({
            'requested_replications': self.requested_replications,
            'measurement_interval': self.measurement_interval,
            'replicating_nodes': replicating_nodes_json
        }, sort_keys=True)