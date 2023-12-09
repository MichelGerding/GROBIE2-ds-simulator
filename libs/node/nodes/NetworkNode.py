from libs.network.Message import Message

from abc import ABC, abstractmethod

class NetworkNode(ABC):

    received_messages: list[str]
    messages_send_counter: int

    def __init__(self, network, node_id, config, x, y, r):
        self.network = network
        self.node_id = node_id
        self.config = config

        self.x = x
        self.y = y
        self.r = r

        network.join_network(self)

        self.received_messages = []
        self.messages_send_counter = 0

    def distance(self, node):
        return ((self.x - node.x) ** 2 + (self.y - node.y) ** 2) ** 0.5

    def rec_message(self, message: Message):
        """ handle messages that are received """
        # if we have already received this message or it is our own we can ignore it
        if message.msg_id in self.received_messages or message.sending_id == self.node_id:
            return

        self.received_messages.append(message.msg_id)

        if message.receiving_id != self.node_id:
            self.propagate_message(message)

        if message.receiving_id == self.node_id or message.receiving_id == 0xFF:
            self.handle_message(message)

    def propagate_message(self, message: Message):
        # TODO:: implement algorithm to propagate messages
        message.hops += 1
        self.network.send_message(message, self)

    @abstractmethod
    def handle_message(self, message: Message):
        """ Handle incoming messages. """
        raise NotImplementedError("Method is abstract and not implemented")

    def __str__(self):
        return f'({self.x}, {self.y}, {self.r})'

    def send_message(self, receiving_id: int, message, channel):
        """ send a message to the network """
        self.network.send_message(Message(
            payload=message,
            sending_id=self.node_id,
            receiving_id=receiving_id,
            channel=channel,
            msg_id=f'{self.node_id}|{self.messages_send_counter}',
        ), self)

        self.messages_send_counter += 1
