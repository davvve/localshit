"""
Service Announcement

Adapted from https://stackoverflow.com/questions/21089268/python-service-discovery-advertise-a-service-across-a-local-network
"""

from socket import *
from select import select
import struct
from utils import StoppableThread
import logging

logging.basicConfig(
    level=logging.DEBUG, format="(%(threadName)-9s) %(message)s",
)


class ServiceDiscovery(StoppableThread):
    hosts = []

    def __init__(self, hosts, UCAST_PORT=10001, MCAST_GRP="224.1.1.1", MCAST_PORT=5007):
        super(ServiceDiscovery, self).__init__()
        self.hosts = hosts
        self.UCAST_PORT = UCAST_PORT
        self.MCAST_GRP = MCAST_GRP
        self.MCAST_PORT = MCAST_PORT
        self.udp_socket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
        try:
            self.udp_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        except AttributeError:
            pass
        self.udp_socket.setsockopt(IPPROTO_IP, IP_MULTICAST_TTL, 1)
        self.udp_socket.setsockopt(IPPROTO_IP, IP_MULTICAST_LOOP, 1)

        self.udp_socket.bind((self.MCAST_GRP, self.MCAST_PORT))

        mreq = struct.pack("4sl", inet_aton(MCAST_GRP), INADDR_ANY)

        self.udp_socket.setsockopt(IPPROTO_IP, IP_ADD_MEMBERSHIP, mreq)

        self.socket_unicast = socket(AF_INET, SOCK_DGRAM)

        hostname = gethostname()
        self.own_addess = gethostbyname(hostname)

    def work_func(self):

        inputready, outputready, exceptready = select([self.udp_socket], [], [], 1)

        for socket_data in inputready:

            data, addr = socket_data.recvfrom(1024)  # wait for a packet
            if data:
                parts = data.decode().split(":")
                if parts[0] == "SA" and addr[0] != self.own_addess:
                    self.add_to_hosts(addr[0])
                    self.socket_unicast.sendto("RP:Hello!".encode(), (addr[0], self.UCAST_PORT))
    
    def add_to_hosts(self, host):
        if host not in self.hosts:
            self.hosts.append(host)
            logging.info("Discovered hosts: %s" % self.hosts)
        else:
            logging.info("Host %s was already discovered" % host)

    def get_hosts(self):
        return hosts

