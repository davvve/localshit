"""
Service Announcement

Adapted from https://stackoverflow.com/questions/21089268/python-service-discovery-advertise-a-service-across-a-local-network
"""

from socket import socket, AF_INET, SOCK_DGRAM
from select import select
from stop import StoppableThread
import logging

logging.basicConfig(
    level=logging.DEBUG, format="(%(threadName)-9s) %(message)s",
)


class ServiceDiscovery(StoppableThread):
    def __init__(self, port):
        super(ServiceDiscovery, self).__init__()
        self.port = port
        self.s = socket(AF_INET, SOCK_DGRAM)  # create UDP socket
        self.s.bind(("", self.port))

    def work_func(self):

        inputready, outputready, exceptready = select([self.s], [], [], 1)
        logging.info("waiting for connection...")

        for socket_data in inputready:

            data, addr = socket_data.recvfrom(1024)  # wait for a packet
            if data:
                logging.info("got service announcement from %s" % data.decode())
