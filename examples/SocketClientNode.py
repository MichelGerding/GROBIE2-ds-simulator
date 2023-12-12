from libs.node.ReplicationInfo import ReplicationInfo
from libs.node.NodeConfig import NodeConfig
from libs.node.nodes.abstracts.BaseNode import BaseNode
from libs.network.Message import Message

import threading
import pickle
import socket
import time


class SocketNode(BaseNode):
    def __init__(self, network: tuple[str, int], node_id, x, y, r):
        super().__init__(node_id, x, y, r)
        self.received_messages = []
        self.messages_send_counter = 0
        self.socket = None

        self.connected = False

        self.connect(network[0], network[1])

        self.listen_thread = threading.Thread(target=self.listen)
        self.listen_thread.daemon = True
        self.listen_thread.start()

    def connect(self, host, port):
        """ connect to a socket """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        info = {
            'node_id': self.node_id,
            'x': self.x,
            'y': self.y,
            'r': self.r
        }

        self.socket.sendall(pickle.dumps(info))
        self.connected = True

    def disconnect(self):
        """ disconnect from the socket """
        self.socket.close()
        self.connected = False

    def listen(self):
        """ listen for messages """
        if not self.connected:
            return

        while True:
            data = self.socket.recv(1024)
            if not data:
                return

            msg = pickle.loads(data)

            self.received_messages.append(msg.msg_id)
            self.rec_message(msg)

    def send_message(self, receiving_id: int, payload, channel):
        """ send a message to the network """
        if not self.connected:
            return

        nid_bytes = self.node_id.to_bytes(2, 'big')
        counter_bytes = self.messages_send_counter.to_bytes(6, 'big')
        msg_id = b'|'.join([nid_bytes, counter_bytes])

        msg = Message(
            receiving_id=receiving_id,
            sending_id=self.node_id,
            channel=channel,
            payload=payload,
            msg_id=msg_id
        )

        msg_bytes = pickle.dumps(msg)
        # send message
        self.socket.sendall(msg_bytes)

        self.messages_send_counter += 1
        time.sleep(0.01)

    def rec_message(self, message):
        if message.sending_id == self.node_id:
            return

        if message.receiving_id == self.node_id or message.receiving_id == 0xFF:
            print(f"Node {self.node_id} received message from {message.sending_id}: {message.payload}")

        # propogate message
        message.hops += 1
        self.send_message(message.receiving_id, message.payload, message.channel)


if __name__ == '__main__':
    node_id = 0x84

    cnf = NodeConfig(5, 2, [ReplicationInfo(node_id, 0)])
    node = SocketNode(('localhost', 8080), node_id, 0, 0, 5)

    while True:
        time.sleep(1)
