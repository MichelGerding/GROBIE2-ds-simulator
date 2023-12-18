import pickle

from libs.node.nodes.abstracts.BaseNode import BaseNode
from libs.network.Message import Message

import multiprocessing.connection as conn

import threading


class ServerSocketNode(BaseNode):
    def __init__(self, network: any, connection: conn.Connection, node_id, x, y, r):
        super().__init__(node_id, x, y, r)
        self.received_messages = []
        self.connection = connection

        self.listen_thread = threading.Thread(target=self.listen)
        self.listen_thread.daemon = True
        self.listen_thread.start()

        print(network)
        self.network = network
        network.join_network(self)

    def listen(self):
        """ listen for messages send by the remote client to send onto the network """
        while True:
            b = self.connection.recv()
            msg = pickle.loads(b)

            self.received_messages.append(msg.msg_id)
            self.send_message(msg)

    def rec_message(self, message: Message):
        # send message over socket
        try:
            self.connection.send(message.serialize())
        except:
            self.shutdown()

    def shutdown(self):
        """ shutdown the node """
        self.connection.close()
        self.network.leave_network(self)

    def send_message(self, message: Message):
        """ send a message to the network """
        # create message
        print(self)

        self.network.send_message(message, self)
