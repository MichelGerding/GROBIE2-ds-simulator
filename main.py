from Network import Message, Network
from AbstractNode import AbstractNode

from random import random
from math import floor
from dataclasses import dataclass

import json


@dataclass
class Measurement:
    temp: float
    light: int

    def __str__(self):
        return json.dumps({
            'temp': self.temp,
            'light': self.light
        }, sort_keys=True)


class RandomNode(AbstractNode):
    def handle_message(self, message: Message):
        print(f'node {self.node_id} got message from node: {message.sending_id}')

    def __init__(self, network: Network, node_id: int, channel: int):
        super().__init__(network, node_id, channel)

    def might_send_message(self, chance=0.75):
        print('send measurement')
        if random() <= chance:
            self.send_measurement()

    def send_measurement(self):
        temp = random() * 5 + 17.5
        light = floor(random() * 1000)

        self.send_message(0xFF, str(Measurement(
            temp, light
        )), 0xFF)


if __name__ == '__main__':
    nodes: list[RandomNode] = []

    network = Network()


    def print_menu():
        cliMenu = """
        | Network simulator menu
        | used to simulate a network of nodes with perfect transmission. 
        | the messages that are received will be logged to the terminal 
        | 
        | the available commands are as follows
        > add new node node: 1 (node_id. ex: 0x44) (channel. ex: 0x01)
        > remove node: 2 (node_id. ex: 0x34)
        > send measurements: 3 (change. ex: 0.75)
        > update config: 4 (requested_replications, update_rate)
        > save all configs to file: 5
        > help (show this menu): h 
        """

        print(chr(27) + "[2J")
        print(cliMenu)
        print_nodes()


    def print_nodes():
        print(f'nodes in network: {", ".join([f"({hex(sub.node_id)}, {hex(sub.channel)})" for sub in network.subscribers])}')


    print_menu()

    while True:
        i = input('> ')
        try:
            if i.startswith('1'):  # add new node
                node_id = int(i.split(' ')[1], 16)
                channel = int(i.split(' ')[2], 16)
                nodes.append(RandomNode(network, node_id, channel))
                print_nodes()

            elif i.startswith('2'):  # remove node
                node_id = int(i.split(' ')[1], 16)
                for i, node in enumerate(nodes):
                    if node.node_id == node_id:
                        del nodes[i]

                print_nodes()

            elif i.startswith('3'):  # send measurements
                chance = float(i.split(' ')[1])
                for node in nodes:
                    node.might_send_message(chance)

            elif i.startswith('4'):  # update config
                print('not implemented')

            elif i.startswith('5'):  # save configs
                print('not implemented')

            elif i.startswith('h'):
                print_menu()

        except Exception as e:
            print(chr(27) + "[2J")
            print_menu()
            print(e)
            print('-' * 48)
