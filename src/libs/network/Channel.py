from enum import Enum


class ChannelID(Enum):
    """ The channel the message is sent on decides if it is configuration or measurement
        0x00 is configuration message
        0x01 is measurement
        0x02 is discovery request
        0x03 is replication bidding message is hops """
    CONFIG = 0x00
    MEASUREMENT = 0x01
    DISCOVERY = 0x02
    REPLICATION_BIDDING = 0x03
    DISCONNECT = 0x04
    CLIENT = 0x05
