import threading
import time
import socket

from libs.network.Message import Message
from libs.node.nodes.BaseNode import BaseNode

import pickle


class ServerSocketNode(BaseNode):

    def __init__(self, network: any, client_socket: socket.socket, node_id, x, y, r):
        super().__init__(node_id, x, y, r)
        self.received_messages = []
        self.socket = client_socket

        self.listen_thread = threading.Thread(target=self.listen)
        self.listen_thread.daemon = True
        self.listen_thread.start()

        self.network = network
        network.join_network(self)

    def listen(self):
        """ listen for messages send by the remote client to send onto the network """
        while True:
            data = self.socket.recv(1024)
            if not data:
                break

            msg = pickle.loads(data)

            self.received_messages.append(msg.msg_id)
            self.send_message(msg)

    def rec_message(self, message):
        # send message over socket
        self.socket.sendall(pickle.dumps(message))

    def send_message(self, message: Message):
        """ send a message to the network """
        # create message
        self.network.send_message(message, self)
