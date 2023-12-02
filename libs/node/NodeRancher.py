from libs.node.nodes.RandomNode import RandomNode
from libs.node.NodeConfig import NodeConfig
from libs.network.Network import Network, Message

import json


class NodeRancher:
    """ Node rancher. control and configure the nodes. """
    nodes: dict[int, RandomNode]

    def __init__(self, network: Network):
        self.network = network
        self.nodes = {}

    def create_node(self, node_id, channel, nodes_replicating):
        """ Create a new node with default config. if node with id exists it will be replaced """

        config = NodeConfig(1, 5, nodes_replicating)
        n = RandomNode(self.network, node_id, channel, config)

        if node_id in self.nodes:
            self.nodes[node_id].stop_measurements()

        self.nodes[node_id] = n
        n.start_measurements()

    def delete_node(self, node_id):
        """ Delete a node """
        del self.nodes[node_id]

    def stop_node(self, node_id=None):
        """
            Stop a node.
            if no node_id is provided we will stop all nodes
        """
        if node_id:
            return self.nodes[node_id].stop_measurements()

        for n in self.nodes.values():
            n.stop_measurements()

    def start_node(self, node_id=None):
        """
            Start a node.
            if no node_id is provided all nodes will be stopped
        """
        if node_id:
            return self.nodes[node_id].start_measurements()

        for n in self.nodes.values():
            n.start_measurements()

    def update_config(self, node_id: int, reps: str, delay: str):
        """ Send message to update nodes config """
        if node_id not in self.nodes:
            print('node not found')
            return

        new_config = NodeConfig(int(reps), int(delay), self.nodes[node_id].config.replicating_nodes)

        self.network.send_message(Message(
            message=str(new_config),
            sending_id=0xFF,
            receiving_id=node_id,
            channel=0x00
        ))

