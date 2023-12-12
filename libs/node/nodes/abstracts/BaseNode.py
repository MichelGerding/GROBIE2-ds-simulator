from abc import ABC, abstractmethod


class BaseNode(ABC):

    def __init__(self, node_id, x, y, r):
        self.node_id = node_id
        self.x = x
        self.y = y
        self.r = r

    @abstractmethod
    def rec_message(self, message):
        """ handle messages that are received """
        raise NotImplementedError("Method is abstract and not implemented")

    def distance(self, node):
        return ((self.x - node.x) ** 2 + (self.y - node.y) ** 2) ** 0.5
