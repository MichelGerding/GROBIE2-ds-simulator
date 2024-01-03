from abc import ABC, abstractmethod
from typing import Callable
class Network(ABC):

    message_callbacks: dict[int, list[callable]]
    routing: Routing
    transceiver: NetworkTransciever

    def __init__(self, routing, transceiver):
        self.message_callbacks = {}
        self.routing = routing
        self.transceiver = transceiver

    @abstractmethod
    def send_message(self, type: int, data: bytes, destination: int = 0xff, channel=0x1) -> None:
        """ Send arbitrary data to a node. """
        # check if data is too long more then 12 mb
        if len(data) > 12 * 1024 * 1024:
            raise ValueError('data is too long')

        next_node = self.routing.get_routing(destination)
        messages = self.compose_message(type=type, destination=destination, data=data)
        for message in messages:
            self.transceiver.send_message(channel=channel, addr=next_node, data=message.serialize())

    def add_callback(self, type, callback: Callable[[Message], None]):
        """ Register a callback for when a message is received. this won't replace a existing callback on a network. """
        if type not in self.message_callbacks:
            self.message_callbacks[type] = []
        self.message_callbacks[type].append(callback)

    def on_receive_message(self, bytes: bytes) -> None:
        """ message is recieved from the network. pass it to the handlers for that type of message. """
        message = self.handle_error(bytes)
        message = Message.deserialize(message)

        if message is None:
            return

        if message.type not in self.message_callbacks:
            return

        for callback in self.message_callbacks[message.type]:
            callback(message)

    @abstractmethod
    def handle_error(self, data: bytes) -> bytes:
        """ detect and correct errors in the message. """
        return data


    @abstractmethod
    def compose_message(self, **kwargs) -> Message:
        """ build the message from the needed parts. this will be actual data send over the network."""
        return Message(**kwargs)



