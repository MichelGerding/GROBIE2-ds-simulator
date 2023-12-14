from libs.node.NodeRancher import NodeRancher

import pickle
import json
import time
import os


class CommandHandler:
    filename = f'tmp/commands/cmds_{time.time()}.txt'

    def __init__(self, nr: NodeRancher):
        self.nr = nr

        # create the file
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)
        self.file = open(self.filename, 'w')

    def handle(self, cwd: str):
        if cwd == '':
            return

        cmd = cwd.split(' ')[0]

        # dynamically call the handler method. this way we can quickly add new commands
        if hasattr(self, 'handle_' + cmd + '_command'):
            # log the command in a file
            self.file.write(cwd + '\n')
            self.file.flush()
            try:
                return getattr(self, 'handle_' + cmd + '_command')(cwd)
            except Exception as e:
                print(f'error while executing command: {cwd}, {e}')
                return 'unknown error'

        else:
            return 'unknown command: ' + cwd

    #######################################
    ########### command handlers ##########
    #######################################
    def handle_save_command(self, cwd):
        """ save the current state of the network to a json file """
        # check if a file name is given
        filename = 'tmp/config.json'
        if len(cwd.split(' ')) > 1:
            filename = cwd.split(' ')[1]

        mode = 'w'
        if filename.endswith('.pickle'):
            mode = 'wb'

        with open(filename, mode) as f:
            nodes_obj = []
            for node in self.nr.nodes.values():
                nodes_obj.append({
                    'node_id': node.node_id,
                    'x': node.x,
                    'y': node.y,
                    'r': node.r,
                    'config': {
                        'measurement_interval': node.config.measurement_interval,
                        'requested_replications': node.config.requested_replications,
                        'replicating_nodes': [i.node_id for i in node.config.replicating_nodes],
                    },
                    'ledger': [
                        {
                            'node_id': key,
                            'requested_replications': value.requested_replications,
                            'replicating_nodes': value.replicating_nodes
                        } for key, value in node.ledger.items()
                    ]
                })

            if filename.endswith('.pickle'):
                return f.write(pickle.dumps(nodes_obj))
            f.write(json.dumps(nodes_obj, default=lambda o: o.__dict__))

    def handle_modify_command(self, cwd):
        """ modify {node_id} {replications} {delay} """
        parts = cwd.split(' ')
        try:
            self.nr.update_config(int(parts[1], 16), parts[2], parts[3])
        except IndexError:
            return 'invalid amount of arguments. 3 arguments are required'
        return f'modified node {parts[1]}'

    def handle_delete_command(self, cwd):
        """ delete a node with the given id
            cmd: `delete {node_id}` """
        parts = cwd.split(' ')
        try:
            node_id = int(parts[1], 16)
        except IndexError:
            return 'invalid amount of arguments. 1 argument is required'

        self.nr.delete_node(node_id)
        return f'deleted node {node_id}'

    def handle_create_command(self, cwd):
        """ create a new node with the given id, position and range.
            cmd: `create {node_id} {x} {y} {range}` """
        parts = cwd.split(' ')
        try:
            node_id = int(parts[1], 16)
            x = int(parts[2])
            y = int(parts[3])
            r = int(parts[4])
        except IndexError:
            return 'invalid amount of arguments'

        self.nr.create_node(node_id, x, y, r)
        return f'created node {node_id}'

    def handle_print_command(self, cwd):
        """ print the network graph to a file or a seperate window. filename is optional
            cmd: `print [filename]`"""
        # save the graph to a image
        g = self.nr.network.graph

        # check if it is we have a extra argument
        if len(cwd.split(' ')) > 1:
            # if we have a extra argument we will use it as the filename
            g.draw(cwd.split(' ')[1])
        else:
            g.draw()

    def handle_load_command(self, cwd):
        """ load a network from a text file
            cmd: `load [filename]` """
        filename = 'cmds_load.txt'
        if len(cwd.split(' ')) > 1:
            filename = cwd.split(' ')[1]

        with open(filename, 'r') as f:
            for line in f.readlines():
                if line.startswith('delay'):
                    time.sleep(int(line.split(' ')[1]))
                    continue

                self.handle(line.strip())

    def handle_exit_command(self, cwd):
        """ exit the program
            cmd: `exit` """
        self.nr.stop_node()
        exit()
