import os
import pickle
import socket

from libs.network.NetworkGraph import NetworkGraph
from libs.network.Message import Message
from libs.node.NodeConfig import NodeConfig
from libs.node.ReplicationInfo import ReplicationInfo
from globals import globals

import threading

from libs.node.nodes.BaseNode import BaseNode
from libs.node.nodes.ServerSocketNode import ServerSocketNode


class Network:
    network_log_file = 'tmp/network_log.txt'

    def __init__(self, port=9174):
        self.graph = NetworkGraph()
        os.makedirs(os.path.dirname(self.network_log_file), exist_ok=True)
        self.file = open(self.network_log_file, 'w')

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.socket_thread = threading.Thread(target=self.start, args=('0.0.0.0', port))
        self.socket_thread.daemon = True
        self.socket_thread.start()

    def start(self, host, port):
        self.sock.bind((host, port))
        self.sock.listen(1)
        print("Listening on port %s" % port)
        while True:
            client_sock, address = self.sock.accept()
            print("Accepted connection from %s" % str(address))
            client_handler = threading.Thread(
                target=self.handle_client_connection,
                args=(client_sock,)
            )
            client_handler.daemon = True
            client_handler.start()

    def handle_client_connection(self, client_socket: socket.socket):
        # first message they send will be their node id, x, y, r
        r = client_socket.recv(1024)
        data = pickle.loads(r)
        node_id = data['node_id']
        x = data['x']
        y = data['y']
        r = data['r']

        globals['ui'].add_text_to_column2(f'node {node_id}, {x}, {y}, {r} connected\n')

        # create a new node
        node = ServerSocketNode(self, client_socket, node_id, x, y, r)
        self.join_network(node)

    def send_message(self, message: Message, node: BaseNode):
        """ send a message to the neighbours of the node """
        globals['ui'].add_text_to_column2(f'sending message to node {message.receiving_id} on channel {message.channel} from {message.sending_id} with {message.hops} hops\n')
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

    def join_network(self, obj: BaseNode):
        """ listen to new messages that have been sent """
        self.graph.add_node(obj)

    def leave_network(self, obj: BaseNode):
        """ stop listening to new messages """
        self.graph.remove_node(obj)
