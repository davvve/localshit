import socket

socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = "127.0.0.1"
port = 10001
buffer_size = 1024

message = "Hello Server"

try:
    socket.sendto(message.encode(), (server_address, port))
    print("Send to server %s" % message)

    print("Waiting for response...")
    data, server = socket.recvfrom(buffer_size)
    print("Received message from server %s" % data.decode())

finally:
    socket.close()
    print("Socket closed")
