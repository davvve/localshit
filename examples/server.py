import socket

socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = "127.0.0.1"
port = 10001
buffer_size = 1024

message = "Hello Client"

print("Server up and running at %s:%s" % (server_address, port))

socket.bind((server_address, port))

while True:
    print("Waiting for message...")

    data, address = socket.recvfrom(buffer_size)
    print("Received message from client %s" % address[0])
    print("Message: %s" % data.decode())

    if data:
        socket.sendto(str.encode(message), address)
        print("Replied to client: %s" % message)
