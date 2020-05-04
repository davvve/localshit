"""
Service Announcement

Adapted from https://stackoverflow.com/questions/21089268/python-service-discovery-advertise-a-service-across-a-local-network
"""

from time import sleep
from socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST
from stop import StoppableThread

import uuid
import logging


logging.basicConfig(
    level=logging.DEBUG, format="(%(threadName)-9s) %(message)s",
)


class ServiceAnnouncement(StoppableThread):
    def __init__(self, port, *args, **kwargs):
        super(ServiceAnnouncement, self).__init__(*args, **kwargs)
        self.port = port
        logging.info("ServiceAnnouncement started")

        self.udp_socket = socket(AF_INET, SOCK_DGRAM)  # create UDP socket
        self.udp_socket.bind(("", 0))
        self.udp_socket.setsockopt(
            SOL_SOCKET, SO_BROADCAST, 1
        )  # this is a broadcast socket
        self.server_id = str(uuid.uuid4())

    def work_func(self):
        try:
            data = self.server_id
            self.udp_socket.sendto(data.encode(), ("<broadcast>", self.port))
            logging.info("sent service announcement")
            sleep(5)
        except Exception as e:
            logging.error("Error: %s" % e)
