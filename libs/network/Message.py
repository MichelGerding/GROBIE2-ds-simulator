from dataclasses import dataclass


@dataclass
class Message:
    # make sure the message arrives at the correct node
    receiving_id: int
    sending_id: int
    channel: int

    payload: str

    # routing info
    msg_id: str
    hops: int = 0