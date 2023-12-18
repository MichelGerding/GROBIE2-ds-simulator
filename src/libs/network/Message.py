from dataclasses import dataclass
import pickle

@dataclass
class Message:
    # make sure the message arrives at the correct node
    receiving_id: int
    sending_id: int
    channel: int

    payload: str

    # routing info
    msg_id: bytes
    ttl: int = 10

    def serialize(self):
        """ serialize a measurement to a string """
        return pickle.dumps(self)

    @staticmethod
    def deserialize(data: bytes):
        """ deserialize a string to a measurement """
        return pickle.loads(data)
