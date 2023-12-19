from random import randint
from typing import Callable

import threading
import math


class ReplicationController:
    """ This class is used to decide which nodes should replicate a measurement. """

    bids: dict[int, int]
    timeout: float
    requested_winners: int
    get_current_replicators: Callable[[], dict[int, int]]

    timer: None | threading.Timer

    def __init__(
            self,
            timeout: float,
            requested_winners: int,
            get_current_replicators: Callable[[], dict[int, int]],
            update_winners: Callable[[dict[int, int]], None]):
        self.bids = {}
        self.timeout = timeout
        self.requested_winners = requested_winners

        self.get_current_replicators = get_current_replicators
        self.update_winners = update_winners

        self.timer = None

    def add_bid(self, node_id: int, bid: int) -> None:
        """ Add a bid to the list of bids. """

        # check if the timer is running
        if self.timer is None or not self.timer.is_alive():
            # start a new timer
            self.timer = threading.Timer(self.timeout, self.decide_winner)
            self.timer.daemon = True
            self.timer.start()

        # add the bid to the list of bids
        self.bids[node_id] = bid

    def decide_winner(self) -> None:
        """ Decide which node should replicate the measurement. """
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

            node = sorted_bids[index]
            winners[node[0]] = node[1]

        # clear the list of bids and update the winners

        self.bids = {}
        self.update_winners(winners)
