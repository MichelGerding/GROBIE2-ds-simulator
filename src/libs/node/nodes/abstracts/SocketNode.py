import pickle
import threading
from abc import ABC, abstractmethod

from libs.network.Channel import ChannelID
from libs.network.Message import Message
from libs.node.nodes.abstracts.BaseNode import BaseNode

from multiprocessing.connection import Connection, Client

class SocketNode(BaseNode, ABC):
    received_messages: list[bytes]
    messages_send_counter: int

    conn: Connection

    def __init__(self, network: tuple[str, int],  node_id: int, x: int, y: int, r: int):
        super().__init__(node_id, x, y, r)

        self.received_messages = []
        self.messages_send_counter = 0

        # set up and connect the socket
        print(f'node {self.node_id} connecting to {network[0]}:{network[1]}')
        self.conn = self.connect(network[0], network[1])

        # start listening to incoming messages
        self.listen_thread = threading.Thread(target=self.listen)
        self.listen_thread.daemon = True
        self.listen_thread.start()

    def rec_message(self, message) -> None:
        # check if we send it or have recieved it earlier
        if message.sending_id == self.node_id or message.msg_id in self.received_messages:
            return

        # propagate the message if it is not only for this node
        if message.receiving_id != self.node_id:
            self.propagate_message(message)

        if message.receiving_id == self.node_id or message.receiving_id == 0xFF:
            self.handle_message(message)

    def propagate_message(self, message: Message) -> None:
        # TODO:: implement better routing algorithm
        message.ttl -= 1
        self.send_message(message.receiving_id, message.payload, message.channel)

    def connect(self, host, port) -> Connection:
        """ connect to a socket and send the node info """
        print(f'node {self.node_id} connecting to {host}:{port}')
        s = Client((host, port))
        s.send({
            'node_id': self.node_id,
            'x': self.x,
            'y': self.y,
            'r': self.r
        })

        print(f'node {self.node_id} connected to {host}:{port}')

        return s

    def disconnect(self) -> None:
        """ disconnect from the socket """
        self.send_message(0xFF, '', ChannelID.DISCONNECT.value)
        self.conn.close()

    def listen(self) -> None:
        """ listen for messages. this function will never finish. """
        while True:
            b = self.conn.recv()
            msg = pickle.loads(b)

            self.rec_message(msg)
            self.received_messages.append(msg.msg_id)

    def send_message(self, receiving_id: int, payload, channel) -> None:
        """ send a message to the network """
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
        self.conn.send(msg_bytes)

        self.messages_send_counter += 1

    @abstractmethod
    def handle_message(self, message: Message):
        """ Handle incoming messages. """
        raise NotImplementedError("Method is abstract and not implemented")
