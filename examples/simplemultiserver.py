import multiprocessing
import socket
import os


class Server(multiprocessing.Process):
    def __init__(self, server_socket, received_data, client_address):
        super(Server, self).__init__()
        self.server_socket = server_socket
        self.received_data = received_data
        self.client_address = client_address

    def run(self):
        message = "Hi %s. This is server %s:%s" % (
            self.client_address[0],
            str(self.client_address[1]),
            str(os.getpid()),
        )
        self.server_socket.sendto(str.encode(message), self.client_address)
        print("Sent to client: %s" % self.client_address[0])


if __name__ == "__main__":
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    server_address = "127.0.0.1"
    server_port = 10001

    buffer_size = 1024

    print("Server up and running at %s:%s" % (server_address, str(server_port)))

    server_socket.bind((server_address, server_port))

    while True:
        data, address = server_socket.recvfrom(buffer_size)
        print(
            "Received message: % at %s:%s"
            % (data.decode(), address[0], str(address[1]))
        )
        p = Server(server_socket, data, address)
        p.start()
        p.join()
