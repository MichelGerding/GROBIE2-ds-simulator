from libs.node.NodeRancher import NodeRancher
from libs.node.NodeConfig import ReplicationInfo
import sys

class CommandHandler:

    def __init__(self, nw: NodeRancher):
        self.nw = nw

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

            self.nw.create_node(node_id, channel, nodes_replicating)

            print('create node')

        elif cwd.startswith('delete'):
            parts = cwd.split(' ')
            node_id = int(parts[1], 16)

            self.nw.delete_node(node_id)

            print('delete node')

        elif cwd.startswith('stop'):
            parts = cwd.split(' ')
            node_id = None
            if len(parts) > 1:
                node_id = int(parts[1], 16)

            self.nw.stop_node(node_id)

            print('stop node')

        elif cwd.startswith('start'):
            parts = cwd.split(' ')
            node_id = None
            if len(parts) > 1:
                node_id = int(parts[1], 16)

            self.nw.start_node(node_id)

            print('start node')

        elif cwd.startswith('mod'):
            parts = cwd.split(' ')

            self.nw.update_config(int(parts[1], 16), parts[2], parts[3])

            print('mod node')

        elif cwd.startswith('save'):
            with open('config.json', 'w') as f:
               # write the json to the file
                f.write('[' + ', '.join([str(i) for i in self.nw.nodes.values()]) +']')

        elif cwd.startswith('exit'):
            sys.exit(0)

        return cwd
