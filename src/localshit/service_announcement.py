"""
Service Announcement

Adapted from https://stackoverflow.com/questions/21089268/python-service-discovery-advertise-a-service-across-a-local-network
"""

from time import sleep
from socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST, IPPROTO_UDP, IP_MULTICAST_TTL, IPPROTO_IP
from stop import StoppableThread

import uuid
import logging


logging.basicConfig(
    level=logging.DEBUG, format="(%(threadName)-9s) %(message)s",
)


class ServiceAnnouncement(StoppableThread):
    def __init__(self, port, MCAST_GRP = '224.1.1.1', MCAST_PORT = 5007):
        super(ServiceAnnouncement, self).__init__()
        self.port = port
        self.MCAST_GRP = MCAST_GRP
        self.MCAST_PORT = MCAST_PORT
        logging.info("ServiceAnnouncement started")

        self.udp_socket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
        self.udp_socket.setsockopt(IPPROTO_IP, IP_MULTICAST_TTL, 32)
        self.server_id = str(uuid.uuid4())

    def work_func(self):
        try:
            data = self.server_id
            self.udp_socket.sendto(data.encode(), (self.MCAST_GRP, self.MCAST_PORT))
            logging.info("sent service announcement")
            sleep(5)
        except Exception as e:
            logging.error("Error: %s" % e)
