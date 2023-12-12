import socket
import threading

import pickle

class SocketServer:
    address_map = {}

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self):
        self.sock.bind((self.host, self.port))
        self.sock.listen(1)
        print("Listening on port %s" % self.port)
        while True:
            client_sock, address = self.sock.accept()
            print("Accepted connection from %s" % str(address))
            client_handler = threading.Thread(
                target=self.handle_client_connection,
                args=(client_sock,)
            )
            client_handler.start()

    def handle_client_connection(self, client_socket: socket.socket):
        # first message they send will be their node id
        node_id = int.from_bytes(client_socket.recv(1024))
        self.address_map[node_id] = client_socket
        print("Received %s" % hex(node_id))

        # all others are of type Message
        while True:
            message = client_socket.recv(1024)
            if not message:
                break

            message = pickle.loads(message)
            print("Received %s" % message.payload)


if __name__ == "__main__":
    server = SocketServer('localhost', 8080)
    server.start()
