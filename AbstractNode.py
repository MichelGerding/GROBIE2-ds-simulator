from abc import abstractmethod, ABC

from Network import Network, Message


class AbstractNode(ABC):
    node_id: int
    channel: int
    network: Network

    def __init__(self, network: Network, node_id: int, channel: int):
        self.network = network
        self.node_id = node_id
        self.channel = channel

        network.subscribe_to_messages(self)

    def on_message(self, message: Message):
        if message.receiving_id != 0xFF and message.receiving_id != self.node_id and message.receiving_id != self.node_id:
            print ('incorrect id ', message.receiving_id, type(message.receiving_id))
            return

        if message.channel != 0xFF and message.channel != self.channel:
            print ('incorrect channel ', message.channel, type(message.channel))
            return

        self.handle_message(message)

    @abstractmethod
    def handle_message(self, message: Message):
        raise NotImplementedError("Method is abstract and not implemented")

    def send_message(self, receiving_id: int, msg: str, channel: int):
        self.network.send_message(Message(
            message=msg,
            sending_id=self.node_id,
            receiving_id=receiving_id,
            channel=channel
        ))
