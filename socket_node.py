import time

from libs.node.ReplicationInfo import ReplicationInfo
from libs.node.nodes.ClientSocketNode import SocketNode
from libs.node.NodeConfig import NodeConfig

if __name__ == '__main__':
    node_id = 0x84

    cnf = NodeConfig(5, 2, [ReplicationInfo(node_id, 0)])
    node = SocketNode(('localhost', 8080), node_id, cnf, 0, 0, 5)

    while True:
        time.sleep(1)
