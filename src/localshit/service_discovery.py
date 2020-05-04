"""
Service Announcement

Adapted from https://stackoverflow.com/questions/21089268/python-service-discovery-advertise-a-service-across-a-local-network
"""

from socket import socket, AF_INET, SOCK_DGRAM
from stop import StoppableThread


class ServiceDiscovery(StoppableThread):
    def __init__(self, port, *args, **kwargs):
        super(ServiceDiscovery, self).__init__(*args, **kwargs)
        self.s = socket(AF_INET, SOCK_DGRAM)  # create UDP socket
        self.s.bind(("", port))

    def worker(self):
        data, addr = self.s.recvfrom(1024)  # wait for a packet
        if data:
            print("got service announcement from %s" % data.decode())

