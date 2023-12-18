from libs.node.nodes.abstracts.SocketNode import SocketNode
from libs.node.ReplicationInfo import ReplicationInfo
from libs.node.nodes.controllers.ConfigController import ConfigController
from libs.network.Channel import ChannelID
from libs.node.NodeConfig import NodeConfig
from libs.network.Message import Message

import multiprocessing.connection as connection


class UserNode(SocketNode):
    """ node that runs in a separate process.
        The functions in this class are almost the same as RandomNode but the node runs in a separate process.
        This is done so that the node can be externally managed or on a different machine.
        The node will connect to the network using a socket connection.
    """

    connection: connection.Connection

    def __init__(self, network: tuple[str, int], node_id: int, cnf: NodeConfig, x: int, y: int, r: int):
        # set up the sockets and the like
        super().__init__(network, node_id, x, y, r)

        self.config_controller = ConfigController(
            node_id,
            cnf,
            lambda message: self.send_message(0xFF, message, ChannelID.CONFIG.value)
        )

        self.send_message(0xFF, self.config_controller.config.serialize(), ChannelID.CONFIG.value)

    ##########################################
    # node functions
    ##########################################
    def handle_message(self, message: Message):
        # check if the node is in the ledger
        if self.node_id == message.sending_id:
            return

        print(f'handling message {message}')

        # call the function that handles messages for the channel
        if hasattr(self, 'handle_' + ChannelID(message.channel).name.lower() + '_message'):
            print(f'handling message on channel {ChannelID(message.channel).name.lower()}', message)
            getattr(self, 'handle_' + ChannelID(message.channel).name.lower() + '_message')(message)
        # else:
        #     print(f'No handler for channel {ChannelID(message.channel).name.lower()}')

    def handle_config_message(self, message: Message):
        """ handle messages that are send by the config controller. """
        self.config_controller.handle_message(message)

    def handle_discovery_message(self, message: Message):
        """ handle messages that are send by the discovery controller. """
        self.config_controller.handle_message(message)

    def handle_client_message(self, message: Message):
        """ handle messages that are send by the user. """
        print(f'handling client message {message.payload}')

    def shutdown(self):
        """ Stop sending measurements to the network. """
        self.disconnect()


if __name__ == '__main__':
    node_id = int(input('node id: ') or 5)

    cnf = NodeConfig(5, 2, {node_id: 0})
    node = UserNode(
        ('localhost', 8080),
        node_id,
        cnf,
        2,
        1,
        5
    )

    try:
        while True:
            n = input('query node > ')
            if n.isnumeric():
                node.send_message(int(n), f'{{"node_id": {n} }}', ChannelID.CLIENT.value)

    except KeyboardInterrupt:
        node.shutdown()
        print('stopped')
