"""
Service Announcement

Adapted from https://stackoverflow.com/questions/21089268/python-service-discovery-advertise-a-service-across-a-local-network
"""

from time import sleep, time
from socket import (
    socket,
    AF_INET,
    SOCK_DGRAM,
    SOL_SOCKET,
    SO_BROADCAST,
    IPPROTO_UDP,
    IP_MULTICAST_TTL,
    IPPROTO_IP,
)
from utils import StoppableThread

import uuid
import logging
from select import select


logging.basicConfig(
    level=logging.DEBUG, format="(%(threadName)-9s) %(message)s",
)


class ServiceAnnouncement(StoppableThread):

    def __init__(self, hosts, port, MCAST_GRP="224.1.1.1", MCAST_PORT=5007):
        super(ServiceAnnouncement, self).__init__()
        self.hosts = hosts
        self.port = port
        self.MCAST_GRP = MCAST_GRP
        self.MCAST_PORT = MCAST_PORT
        logging.info("ServiceAnnouncement started")

        self.udp_socket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
        self.udp_socket.setsockopt(IPPROTO_IP, IP_MULTICAST_TTL, 32)
        self.server_id = str(uuid.uuid4())

        self.socket_unicast = socket(AF_INET, SOCK_DGRAM)
        self.socket_unicast.bind(("0.0.0.0", 10001))

        self.service_announcement()

    def work_func(self):
        try:
            inputready, outputready, exceptready = select([self.socket_unicast], [], [], 1)

            for socket_data in inputready:

                data, addr = socket_data.recvfrom(1024)
                if data:
                    parts = data.decode().split(":")

                    if parts[0] == "RP":
                        self.add_to_hosts(addr[0])


        except Exception as e:
            logging.error("Error: %s" % e)

    def service_announcement(self):
        data = "%s:%s:%s" % ("SA", self.server_id, "Hello World!")
        self.udp_socket.sendto(data.encode(), (self.MCAST_GRP, self.MCAST_PORT))
        logging.info("service announcement...")

    def add_to_hosts(self, host):
        if host not in self.hosts:
            self.hosts.append(host)
            logging.info("Discovered hosts: %s" % self.hosts)

