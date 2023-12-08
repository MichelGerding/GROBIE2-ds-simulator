from abc import ABC, abstractmethod

from libs.network.Message import Message


class NetworkNode(ABC):

    def __init__(self, network, node_id, config, x, y, r):
        self.network = network
        self.node_id = node_id
        self.config = config

        self.x = x
        self.y = y
        self.r = r

        network.join_network(self)

    def distance(self, node):
        return ((self.x - node.x) ** 2 + (self.y - node.y) ** 2) ** 0.5

    def rec_message(self, message: Message):
        """ handle messages that are received """
        # if it is our own message we can ignore it
        if message.sending_id == self.node_id:
            return

        # TODO:: propagate the message if not for us.
        self.handle_message(message)

    @abstractmethod
    def handle_message(self, message: Message):
        """ Handle incoming messages. """
        raise NotImplementedError("Method is abstract and not implemented")

    def __str__(self):
        return f'({self.x}, {self.y}, {self.r})'

    def send_message(self, receiving_id, message, channel):
        """ send a message to the network """
        self.network.send_message(Message(
            message=message,
            sending_id=self.node_id,
            receiving_id=receiving_id,
            channel=channel
        ), self)
