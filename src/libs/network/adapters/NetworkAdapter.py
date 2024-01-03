from abc import ABC, abstractmethod

from libs.network.Message import Message


class NetworkAdapter(ABC):
    """ Abstract class for network adapters. """

    message_callbacks: dict[int, list[callable]]

    def __init__(self):
        self.message_callbacks = {}

    @abstractmethod
    def send_message(self, message: bytes, receiving_id: int) -> None:
        """ Send a message to a node. """
        raise NotImplementedError

    def register_message_callback(self, type, callback):
        """ Register a callback for when a message is received. this won't replace a existing callback on a network. """
        if type not in self.message_callbacks:
            self.message_callbacks[type] = []
        self.message_callbacks[type].append(callback)


    def receive_message(self) -> None:
        """ Receive a message from a node. """

    @abstractmethod
    def join_network(self, node) -> None:
        """ Join a network. """
        raise NotImplementedError

    @abstractmethod
    def leave_network(self, node) -> None:
        """ Leave a network. """
        raise NotImplementedError
