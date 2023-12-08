from dataclasses import dataclass


@dataclass
class Message:
    # make sure the message arrives at the correct node
    receiving_id: int
    sending_id: int
    channel: int

    message: str
