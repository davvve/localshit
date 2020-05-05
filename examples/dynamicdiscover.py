import socket


def broadcast(IP, PORT, broadcast_message):
    broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    # broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    broadcast_socket.sendto(str.encode(broadcast_message), (IP, PORT))
    broadcast_socket.close()


if __name__ == "__main__":
    BROADCAST_IP = "172.17.255.255"
    BROADCAST_PORT = 5000

    MY_HOST = socket.gethostname()
    MY_IP = socket.gethostbyname(MY_HOST)

    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listen_socket.bind((BROADCAST_IP, BROADCAST_PORT))

    message = "I'm new!"
    broadcast(BROADCAST_IP, BROADCAST_PORT, message)

    print("Listening to broadcast messages")

    while True:
        data, addr = listen_socket.recvfrom(1024)
        if data:
            if addr[0] != MY_IP:
                response = data.decode()
                print("Received broadcast message: %s from %s" % (response, addr[0]))
                if "I'm new!" in response:
                    message = "Hello!"
                    broadcast(BROADCAST_IP, BROADCAST_PORT, message)
