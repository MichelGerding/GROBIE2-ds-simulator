from libs.network.Message import Message

from abc import ABC, abstractmethod

from libs.node.nodes.BaseNode import BaseNode


class NetworkNode(BaseNode, ABC):

    received_messages: list[bytes]
    messages_send_counter: int

    def __init__(self, network, node_id, x, y, r):
        super().__init__(node_id, x, y, r)

        self.network = network
        self.node_id = node_id

        self.x = x
        self.y = y
        self.r = r

        self.received_messages = []
        self.messages_send_counter = 0

        network.join_network(self)

    def rec_message(self, message: Message):
        """ handle messages that are received """
        # if the message was our own message, ignore it
        if message.sending_id == self.node_id:
            return

        # check if we already received the message
        if message.msg_id in self.received_messages:
            return

        self.received_messages.append(message.msg_id)

        if message.receiving_id != self.node_id:
            self.propagate_message(message)

        if message.receiving_id == self.node_id or message.receiving_id == 0xFF:
            self.handle_message(message)

    def propagate_message(self, message: Message):
        # TODO:: implement efficient routing algorithm
        message.hops += 1
        self.network.send_message(message, self)

    @abstractmethod
    def handle_message(self, message: Message):
        """ Handle incoming messages. """
        raise NotImplementedError("Method is abstract and not implemented")

    def __str__(self):
        return '({self.x}, {self.y}, {self.r})'

    def send_message(self, receiving_id: int, payload, channel):
        """ send a message to the network """

        # create a message id which consists of the node id and a counter converted to bytes seperated with '|'
        nid_bytes = self.node_id.to_bytes(2, 'big')
        counter_bytes = self.messages_send_counter.to_bytes(6, 'big')
        msg_id = b'|'.join([nid_bytes, counter_bytes])

        self.network.send_message(Message(
            payload=payload,
            sending_id=self.node_id,
            receiving_id=receiving_id,
            channel=channel,
            msg_id=msg_id,
        ), self)

        self.messages_send_counter += 1
