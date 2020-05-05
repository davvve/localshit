import socket
import multiprocessing
import os


def send_message(server_address, server_port):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        message = "Hi from %s as %s:%s" % (
            str(os.getpid()),
            server_address,
            str(server_port),
        )

        client_socket.sendto(str.encode(message), (server_address, server_port))
        print("Sent to server: %s" % message)

        print("Waiting for response...")
        data, server = client_socket.recvfrom(1024)
        print("Received message: %s" % data.decode())

    finally:
        client_socket.close()
        print("Socket closed")


if __name__ == "__main__":

    server_address = "127.0.0.1"
    server_port = 10001

    for i in range(3):
        p = multiprocessing.Process(
            target=send_message, args=(server_address, server_port)
        )
        p.start()
        p.join()
