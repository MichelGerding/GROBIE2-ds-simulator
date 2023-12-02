import jsonpickle

from libs.node.NodeRancher import NodeRancher
from libs.node.NodeConfig import ReplicationInfo
import json
import sys


class CommandHandler:

    def __init__(self, nr: NodeRancher):
        self.nr = nr

    def handle(self, cwd: str):
        if cwd == '':
            return

        if cwd.startswith('create'):
            # get the node id and channel
            parts = cwd.split(' ')
            node_id = int(parts[1], 16)
            channel = int(parts[2], 16)
            try:
                nodes_replicating = [ReplicationInfo(int(i, 16), 1) for i in parts[3].split(',')]
            except:
                nodes_replicating = []

            self.nr.create_node(node_id, channel, nodes_replicating)

            print('create node')

        elif cwd.startswith('delete'):
            parts = cwd.split(' ')
            node_id = int(parts[1], 16)

            self.nr.delete_node(node_id)

            print('delete node')

        elif cwd.startswith('stop'):
            parts = cwd.split(' ')
            node_id = None
            if len(parts) > 1:
                node_id = int(parts[1], 16)

            self.nr.stop_node(node_id)

            print('stop node')

        elif cwd.startswith('start'):
            parts = cwd.split(' ')
            node_id = None
            if len(parts) > 1:
                node_id = int(parts[1], 16)

            self.nr.start_node(node_id)

            print('start node')

        elif cwd.startswith('mod'):
            parts = cwd.split(' ')

            self.nr.update_config(int(parts[1], 16), parts[2], parts[3])

            print('mod node')

        elif cwd.startswith('save'):
            with open('config.json', 'w') as f:
                # write the json to the file
                nodes_obj = []
                for node in self.nr.nodes.values():
                    nodes_obj.append({
                        'node_id': node.node_id,
                        'channel': node.channel,
                        'config': {
                            'measurement_interval': node.config.measurement_interval,
                            'requested_replications': node.config.requested_replications,
                            'replicating_nodes': [i.node_id for i in node.config.replicating_nodes]
                        },
                        'ledger': [
                            {
                                'node_id': key,
                                'requested_replications': value.requested_replications,
                                'replicating_nodes': [i for i in value.replicating_nodes]
                            } for key, value in node.ledger.items()
                        ]
                    })

                f.write(json.dumps(nodes_obj))

        elif cwd.startswith('exit'):
            sys.exit(0)

        return cwd
