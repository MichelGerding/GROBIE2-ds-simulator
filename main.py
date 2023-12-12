import argparse

from libs.network.networks.Network import Network
from libs.node.NodeRancher import NodeRancher
from libs.CommandHandler import CommandHandler
from libs.TerminalUI import TerminalUI
from libs.Logger import Logger
from globals import globals


def setup_ui(command_handler: CommandHandler):
    help_message = ("command log \n"
                    "create (node_id) (x) (y) (power):     create nodes\n"
                    "del (node):                            delete node\n"
                    "mod (node) (replications) (delay):   modify config\n"
                    "save/print [filepath]:save config/network to file")
    globals['ui'] = TerminalUI(help_message, "Network log", command_handler)


def start_ui():
    try:
        globals['ui'].draw()
        print('press enter to quit')
        globals['ui'].run()
    except KeyboardInterrupt:
        pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=9174)
    args = parser.parse_args()

    # initialization
    globals['logger'] = Logger('tmp/log.txt')

    network = Network(args.port)
    nw = NodeRancher(network)
    chd = CommandHandler(nw)

    # setup
    setup_ui(chd)

    # start
    # !!!!!!!!!! BLOCKING WHILE LOOP !!!!!!!!!!!!
    start_ui()

    # shutdown
    nw.stop_node()

if __name__ == '__main__':
    main()
