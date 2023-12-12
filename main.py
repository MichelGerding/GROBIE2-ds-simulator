import argparse
import sys

from libs.network.networks.Network import Network
from libs.node.NodeRancher import NodeRancher
from libs.CommandHandler import CommandHandler
from libs.TerminalUI import TerminalUI
from libs.Logger import Logger
from globals import globals


def setup_ui(command_handler: CommandHandler):
    help_message = ("command log \n"
                    "load [file]                 run commands from file\n"
                    "create (node_id) (x) (y) (power)      create nodes\n"
                    "delete (node_id)                       delete node\n"
                    "modify (node) (replications) (delay) modify config\n"
                    "save/print [file]      save config/network to file")
    return TerminalUI(help_message, "Network log", command_handler)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=9174)
    parser.add_argument('--log', type=str, default='tmp/log.txt')
    args = parser.parse_args()
    return args

def main():
    args = parse_args()
    globals['args'] = args

    # setup logger to capture stdout.
    sys.stdout = Logger(args.log)

    # setup network, node rancher and command handler
    network = Network(args.port)
    nw = NodeRancher(network)
    chd = CommandHandler(nw)
    globals['ui'] = setup_ui(chd)


    # draw and run the ui
    try:
        globals['ui'].draw()
        globals['ui'].run()  # blocking
    except KeyboardInterrupt:
        pass

    # shutdown
    nw.stop_node()

if __name__ == '__main__':
    main()
