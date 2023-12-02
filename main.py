from libs.network.Network import Network
from libs.node.NodeRancher import NodeRancher
from libs.CommandHandler import CommandHandler

from libs.TerminalUI import TerminalUI

from globals import globals


def setup_ui(command_handler: CommandHandler):
    help_message = ("command log \n"
                    "create (node_id) (channel):    create a new node\n"
                    "del (node_id):                 delete node\n"
                    "mod (node_id) (key) (new_val): modify config\n"
                    "save:                          save config to file\n"
                    "stop [node_id]:             stop all/selected node\n"
                    "exit:                          exit program\n")
    globals['ui'] = TerminalUI(help_message, "Network log", command_handler)


def start_ui():
    try:
        globals['ui'].draw()
        print('press enter to quit')
        globals['ui'].run()
    except KeyboardInterrupt:
        pass


def main():
    # init
    network = Network()
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
