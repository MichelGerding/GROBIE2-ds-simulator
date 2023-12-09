import os

from libs.network.NetworkGraph import NetworkGraph
from libs.network.Message import Message
from libs.node.nodes import NetworkNode
from globals import globals

class Network:
    network_log_file = 'tmp/network_log.txt'

    def __init__(self):
        self.graph = NetworkGraph()
        os.makedirs(os.path.dirname(self.network_log_file), exist_ok=True)
        self.file = open(self.network_log_file, 'w')

    def send_message(self, message: Message, node: NetworkNode):
        """ send a message to the neighbours of the node """
        globals['ui'].add_text_to_column2(f'sending message to node {message.receiving_id} on channel {message.channel} from {message.sending_id} with {message.hops} hops]\n')
        # log into file
        mess_dict = {
            'sending_id': message.sending_id,
            'receiving_id': message.receiving_id,
            'channel': message.channel,
            'hops': message.hops,
            'payload': message.payload
        }
        self.file.write(str(mess_dict) + '\n')
        self.file.flush()

        # send the message to the neighbours of the node
        for n in self.graph.get_neighbours(node):
            n.rec_message(message)

    def join_network(self, obj: NetworkNode):
        """ listen to new messages that have been sent """
        self.graph.add_node(obj)

    def leave_network(self, obj: NetworkNode):
        """ stop listening to new messages """
        self.graph.remove_node(obj)
