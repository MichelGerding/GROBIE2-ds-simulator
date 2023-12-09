from libs.network.NetworkGraph import NetworkGraph
from libs.network.Message import Message
from libs.node.nodes import NetworkNode
from globals import globals

class Network:

    def __init__(self):
        self.graph = NetworkGraph()

    def send_message(self, message: Message, node: NetworkNode):
        """ send a message to the neighbours of the node """
        globals['ui'].add_text_to_column2(f'sending message to node {message.receiving_id} on channel {message.channel} from {message.sending_id} with {message.hops} hops]\n')

        # send the message to the neighbours of the node
        for n in self.graph.get_neighbours(node):
            n.rec_message(message)

    def join_network(self, obj: NetworkNode):
        """ listen to new messages that have been sent """
        self.graph.add_node(obj)

    def leave_network(self, obj: NetworkNode):
        """ stop listening to new messages """
        self.graph.remove_node(obj)
