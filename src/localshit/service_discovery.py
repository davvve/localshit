"""
Service Announcement

Adapted from https://stackoverflow.com/questions/21089268/python-service-discovery-advertise-a-service-across-a-local-network
"""

from socket import *
from select import select
import struct
from stop import StoppableThread
import logging

logging.basicConfig(
    level=logging.DEBUG, format="(%(threadName)-9s) %(message)s",
)


class ServiceDiscovery(StoppableThread):
    def __init__(self, port, MCAST_GRP = '224.1.1.1', MCAST_PORT = 5007):
        super(ServiceDiscovery, self).__init__()
        self.port = port
        self.MCAST_GRP = MCAST_GRP
        self.MCAST_PORT = MCAST_PORT
        self.udp_socket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
        try:
            self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except AttributeError:
            pass
        # self.udp_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32) 
        # self.udp_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)

        self.udp_socket.bind((self.MCAST_GRP, self.MCAST_PORT))

        mreq = struct.pack("4sl", inet_aton(MCAST_GRP), INADDR_ANY)

        self.udp_socket.setsockopt(IPPROTO_IP, IP_ADD_MEMBERSHIP, mreq)


    def work_func(self):

        inputready, outputready, exceptready = select([self.udp_socket], [], [], 1)
        logging.info("waiting for connection...")

        for socket_data in inputready:

            data, addr = socket_data.recvfrom(1024)  # wait for a packet
            if data:
                logging.info("got service announcement from %s:%s with id %s" % (addr[0], addr[1], data.decode()))
