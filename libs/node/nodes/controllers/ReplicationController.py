from libs.node.ReplicationInfo import ReplicationInfo

from random import randint
from typing import Callable

import threading
import math


class ReplicationController:
    """ This class is used to decide which nodes should replicate a measurement. """

    bids: dict[int, int]
    timeout: float
    requested_winners: int
    get_current_replicators: Callable[[], list[ReplicationInfo]]

    timer: None | threading.Timer

    def __init__(
            self,
            timeout: float,
            requested_winners: int,
            get_current_replicators: Callable[[], list[ReplicationInfo]],
            update_winners: Callable[[list[ReplicationInfo]], None]):
        self.bids = {}
        self.timeout = timeout
        self.requested_winners = requested_winners

        self.get_current_replicators = get_current_replicators
        self.update_winners = update_winners

        self.timer = None

    def add_bid(self, node_id: int, bid: int):
        """ Add a bid to the list of bids. """

        # check if the timer is running
        if self.timer is None or not self.timer.is_alive():
            # start a new timer
            self.timer = threading.Timer(self.timeout, self.decide_winner)
            self.timer.daemon = True
            self.timer.start()

        # add the bid to the list of bids
        self.bids[node_id] = bid

    def decide_winner(self):
        """ Decide which node should replicate the measurement. """
        # TODO:: implement better algorithm to decide which nodes should replicate the measurement
        winners = self.get_current_replicators()
        winner_count = self.requested_winners - len(winners)

        if winner_count <= 0:
            return

        # sort the bids
        sorted_bids = sorted(self.bids.items(), key=lambda x: x[1], reverse=True)

        segment_size = len(sorted_bids) // winner_count
        if segment_size == 0:
            # take all bids
            segment_size = 1

        for i in range(min(winner_count, math.ceil(len(sorted_bids) / segment_size))):
            index = randint(i * segment_size, (i + 1) * segment_size - 1)

            node = sorted_bids[index][0]
            if node not in winners:
                # append the node and the amount of hops it is away from the node that send the measurement
                winners.append(ReplicationInfo(node, sorted_bids[index][1]))

        # clear the list of bids and update the winners

        self.bids = {}
        self.update_winners(winners)
