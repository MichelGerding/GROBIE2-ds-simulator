from dataclasses import dataclass

import json


@dataclass
class ReplicationInfo:
    node_id: int
    hops: int

    def __str__(self):
        return json.dumps({
            'node_id': self.node_id,
            'hops': self.hops
        }, sort_keys=True)