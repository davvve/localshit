import multiprocessing
import socket
import os


def send_message(server_socket, client_address):
    message = "Hi %s. This is server %s:%s" % (
        client_address[0],
        str(client_address[1]),
        str(os.getpid()),
    )
    server_socket.sendto(str.encode(message), client_address)
    print("Sent to client: %s" % client_address)


def test(x):
    return x * x


if __name__ == "__main__":
    number_processes = 4
    pool = multiprocessing.Pool(number_processes)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    server_address = "127.0.0.1"
    server_port = 10001

    buffer_size = 1024

    print("Server up and running at %s:%s" % server_address, str(server_port))

    server_socket.bind((server_address, server_port))

    while True:
        data, address = server_socket.recvfrom(buffer_size)
        print(
            "Received message: % at %s:%s"
            % (data.decode(), address[0], str(address[1]))
        )
        pool.apply_async(send_message, args=(server_socket, address,))
