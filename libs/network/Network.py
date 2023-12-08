from libs.network.Message import Message
from libs.node.nodes import NetworkNode
from globals import globals

import matplotlib.pyplot as plt
import networkx as nx

import matplotlib


class NetworkGraph:
    """ This is a graph of the network.
        It is used to keep track of the nodes and their connections.
        this uses the networkx library to create a graph. """

    def __init__(self):
        self.graph = nx.DiGraph()

    def add_node(self, node: NetworkNode):
        self.graph.add_node(node)
        # get all nodes that are within range of the new node
        for n in self.graph.nodes:
            self.update_neighbours(n)

    def update_neighbours(self, node: NetworkNode):
        # get all nodes that are within range of the new node
        nodes = list(self.graph.nodes)  # Create a copy of the nodes

        # loop over all nodes and check if they need to update their neighbours
        for n in nodes:
            if n.distance(node) <= n.r and n != node:
                self.graph.add_edge(n, node, weight=n.distance(node))

    def remove_node(self, node: NetworkNode):
        self.graph.remove_node(node.node_id)

    def get_neighbours(self, node: NetworkNode):
        """ get all neighbours of the node """
        return list(self.graph.neighbors(node))

    def draw(self, file_name=None):
        """ draw the graph with the actual positions and ranges"""
        pos = {node: (node.x, node.y) for node in self.graph.nodes}

        labels = {node: f"{node.node_id}\nRadius: {node.r}" for node in self.graph.nodes}

        # Create a colormap based on the range values
        # cmap = plt.cm.get_cmap('viridis') # You can choose a different colormap
        cmap = matplotlib.colormaps['viridis']
        norm = plt.Normalize(vmin=min(node.r for node in self.graph.nodes),
                             vmax=max(node.r for node in self.graph.nodes))

        fig, ax = plt.subplots(figsize=(8, 8))

        # Draw nodes with colors based on the radius
        nx.draw_networkx_nodes(self.graph, pos=pos, node_size=300,
                               node_color=[cmap(norm(node.r)) for node in self.graph.nodes], ax=ax)
        nx.draw_networkx_edges(self.graph, pos=pos, ax=ax)
        nx.draw_networkx_labels(self.graph, pos, labels, font_size=8, font_color="black", ax=ax)

        # Draw circles to represent node radius with the color based on the node range
        for node, (x, y) in pos.items():
            circle = plt.Circle((x, y), node.r, color=cmap(norm(node.r)), fill=False)
            ax.add_patch(circle)

        ax.set_title("Network topology")
        fig.tight_layout()

        if file_name:
            fig.savefig(file_name)
        else:
            plt.show()


class Network:

    def __init__(self):
        self.graph = NetworkGraph()

    def send_message(self, message: Message, node: NetworkNode):
        """ send a message to the neighbours of the node """
        globals['ui'].add_text_to_column2(f'sending message to node {message.receiving_id} on channel {message.channel} from {message.sending_id}')
        # print(f'sending message to node {message.receiving_id} on channel {message.channel} from {message.sending_id}')

        # send the message to the neighbours of the node
        for n in self.graph.get_neighbours(node):
            n.rec_message(message)

    def join_network(self, obj: NetworkNode):
        """ listen to new messages that have been sent """
        self.graph.add_node(obj)

    def leave_network(self, obj: NetworkNode):
        """ stop listening to new messages """
        self.graph.remove_node(obj)
