from dataclasses import dataclass



@dataclass
class Message:
    # make sure the message arrives at the correct node
    receiving_id: int
    sending_id: int
    channel: int

    message: str


class Network:
    last_message: None | str = None

    def __init__(self):
        self.subscribers = []

    def send_msg(self, msg: str, sending_id: int, receiving_id: int, channel: int):
        """ send a message onto the network """
        print(f'sending message to node {receiving_id} on channel {channel} from {sending_id}')

        self.notify_subscribers(Message(
            receiving_id, sending_id, channel, message=msg
        ))

    def send_message(self, message: Message):
        self.notify_subscribers(message)

    def notify_subscribers(self, msg: Message):
        """ notify all subscribers of a new message"""
        for s in self.subscribers:
            s.on_message(msg)

    def subscribe_to_messages(self, obj):
        """ listen to new messages that have been sent """
        self.subscribers.append(obj)

    def unsubscribe(self,obj):
        index = self.subscribers.index(obj)
        self.subscribers.pop(index)


