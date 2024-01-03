import os
import multiprocessing.connection as conn
import random

from libs.network.Channel import ChannelID
from libs.network.NetworkGraph import NetworkGraph
from libs.network.Message import Message
from globals import globals

import threading

from libs.node.nodes.abstracts.BaseNode import BaseNode
from libs.node.nodes.ServerSocketNode import ServerSocketNode


def corrupt_bytes(message: bytes, chance=0.0001) -> bytes:
    """ Modify one or more random bits in the message. """
    new_bytes = b''

    # loop over each bit
    for b in message:
        # convert to binary
        b = bin(b)[2:].zfill(8)

        # loop over each bit in the byte
        for i in range(8):
            # get a random number between 0 and 1
            r = random.random()

            # if the random number is smaller than the chance we will flip the bit
            if r < chance:
                # flip the bit
                b = b[:i] + str(int(not bool(int(b[i])))) + b[i+1:]

        # convert back to bytes
        new_bytes += int(b, 2).to_bytes(1, 'big')

    return new_bytes


class Network:
    network_log_file = 'tmp/network_log.txt'

    def __init__(self, port=9174):
        self.graph = NetworkGraph()
        os.makedirs(os.path.dirname(self.network_log_file), exist_ok=True)
        self.file = open(self.network_log_file, 'w')

        # setup connectioin using multiprocessing.connection
        self.socket_thread = threading.Thread(target=self.start, args=('0.0.0.0', port))
        self.socket_thread.daemon = True
        self.socket_thread.start()

    def start(self, host, port):
        # open a connection using multiprocessing.connection

        listener = conn.Listener((host, port))
        print('listening on', listener.last_accepted)
        while True:
            client = listener.accept()
            print('connection accepted from', listener.last_accepted)
            client_handler = threading.Thread(
                target=self.handle_client_connection,
                args=(client,)
            )
            client_handler.daemon = True
            client_handler.start()


    def handle_client_connection(self, client_socket: conn.Connection):
        # first message they send will be their node id, x, y, r
        data = client_socket.recv()
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
        # globals['ui'].add_text_to_column2(f'sending message to node {message.receiving_id} on channel {message.channel} from {message.sending_id} with {message.ttl} hops\n')
        # log into file
        mess_dict = {
            'sending_id': message.sending_id,
            'receiving_id': message.receiving_id,
            'channel': message.channel,
            'hops': message.ttl,
            'payload': message.payload
        }
        self.file.write(str(mess_dict) + '\n')
        self.file.flush()

        # send the message to the neighbours of the node
        # check if node is in the graph
        if node not in self.graph.graph.nodes:
            return

        # corrupt the payload
        message.payload = corrupt_bytes(message.payload, 0)

        for n in self.graph.get_neighbours(node):
            n.rec_message(message)

        if message.channel == ChannelID.DISCONNECT.value and message.sending_id == node.node_id:
            # disconnect node
            self.leave_network(node)

    def join_network(self, obj: BaseNode):
        """ listen to new messages that have been sent """
        self.graph.add_node(obj)

    def leave_network(self, obj: BaseNode):
        """ stop listening to new messages """
        self.graph.remove_node(obj)
