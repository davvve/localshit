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
    gethostname,
    gethostbyname
)
from select import select
import uuid
import logging

from utils import StoppableThread

logging.basicConfig(
    level=logging.DEBUG, format="(%(threadName)-9s) %(message)s",
)


class ServiceAnnouncement(StoppableThread):

    def __init__(self, hosts, UCAST_PORT=10001, MCAST_GRP="224.1.1.1", MCAST_PORT=5007):
        super(ServiceAnnouncement, self).__init__()
        self.hosts = hosts
        self.UCAST_PORT = UCAST_PORT
        self.MCAST_GRP = MCAST_GRP
        self.MCAST_PORT = MCAST_PORT

        self.socket_multicast = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
        self.socket_multicast.setsockopt(IPPROTO_IP, IP_MULTICAST_TTL, 32)
        self.server_id = str(uuid.uuid4())

        self.socket_unicast = socket(AF_INET, SOCK_DGRAM)
        self.socket_unicast.bind(("0.0.0.0", 10001))

        hostname = gethostname()
        self.own_addess = gethostbyname(hostname)

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
        data = "%s:%s" % ("SA", self.server_id)
        self.socket_multicast.sendto(data.encode(), (self.MCAST_GRP, self.MCAST_PORT))
        logging.info("service announcement...")

    def add_to_hosts(self, host):
        self.hosts.add_host(host, self.own_addess)

