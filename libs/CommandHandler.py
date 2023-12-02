from libs.node.NodeRancher import NodeRancher
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

            self.nw.create_node(node_id, channel)

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
            with open('config.csv', 'w') as f:
                f.write('node_id,channel,measurement_interval,requested_replications\n')

                for node in self.nw.nodes.values():
                    f.write(f'{str(node.node_id)},{str(node.channel)},{str(node.config.measurement_interval)},{str(node.config.requested_replications)}\n')

        elif cwd.startswith('exit'):
            sys.exit(0)

        return cwd
