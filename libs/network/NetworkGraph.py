
from matplotlib import pyplot as plt

import networkx as nx

import matplotlib

from libs.node.nodes.abstracts.BaseNode import BaseNode


class NetworkGraph:
    """ This is a graph of the network.
        It is used to keep track of the nodes and their connections.
        this uses the networkx library to create a graph. """

    def __init__(self):
        self.graph = nx.DiGraph()

    def add_node(self, node: BaseNode):
        """ add a node to the graph. this will also recompute the neighbours of the nodes."""
        self.graph.add_node(node)
        # get all nodes that are within range of the new node
        for n in self.graph.nodes:
            self.update_neighbours(n)

    def update_neighbours(self, node: BaseNode):
        """ update the neighbours of the node """
        # get all nodes that are within range of the new node
        nodes = list(self.graph.nodes)  # Create a copy of the nodes

        # loop over all nodes and check if they need to update their neighbours
        for n in nodes:
            if n.distance(node) <= n.r and n != node:
                self.graph.add_edge(n, node, weight=n.distance(node))

    def remove_node(self, node: BaseNode):
        """ remove a node from the graph."""
        # remove all edges to the node
        for n in self.get_neighbours(node):
            if n == node:
                continue

            if self.graph.has_edge(n, node):
                self.graph.remove_edge(n, node)
            if self.graph.has_edge(node, n):
                self.graph.remove_edge(node, n)

        # delete the node
        self.graph.remove_node(node)

    def get_neighbours(self, node: BaseNode):
        """ get all neighbours of the node """
        return list(self.graph.neighbors(node))

    def draw(self, file_name=None):
        """ draw the graph with the actual positions and ranges.
            if given a file_name it will save the graph to a file. """


        # check if there are nodes in the graph
        if len(self.graph.nodes) == 0:
            return

        # Create dictionaries with the positions and labels of the nodes
        pos = {node: (node.x, node.y) for node in self.graph.nodes}
        labels = {node: f"{node.node_id}\nRadius: {node.r}" for node in self.graph.nodes}

        # Create a colormap based on the range values
        cmap = matplotlib.colormaps['viridis']
        norm = plt.Normalize(vmin=min(node.r for node in self.graph.nodes),
                             vmax=max(node.r for node in self.graph.nodes))

        # Create the figure and axes
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

        # Set the title and make the layout tight
        ax.set_title("Network topology")
        ax.axis('equal')
        fig.tight_layout()

        # Save the figure to a file or show it
        if file_name:
            fig.savefig(file_name)
        else:
            plt.show()
