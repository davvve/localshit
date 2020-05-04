"""
Service Announcement

Adapted from https://stackoverflow.com/questions/21089268/python-service-discovery-advertise-a-service-across-a-local-network
"""

from socket import socket, AF_INET, SOCK_DGRAM


class ServiceDiscovery:
    def __init__(self, port):
        # MAGIC = "fna349fn"
        s = socket(AF_INET, SOCK_DGRAM) #create UDP socket
        s.bind(('', port))

        while True:
            data, addr = s.recvfrom(1024) #wait for a packet
            if data:
                print("got service announcement from %s" % data.decode())



if __name__ == "__main__":
    print("service discovery...")
    app = ServiceDiscovery(5000)