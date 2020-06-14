"""
Service Announcement

Adapted from https://stackoverflow.com/questions/21089268/python-service-discovery-advertise-a-service-across-a-local-network
"""

from select import select
from utils import StoppableThread
from utils import utils
import logging

logging.basicConfig(
    level=logging.DEBUG, format="(%(threadName)-9s) %(message)s",
)


class ServiceDiscovery(StoppableThread):
    def __init__(self, hosts, UCAST_PORT=10001, MCAST_GRP="224.1.1.1", MCAST_PORT=5007):
        super(ServiceDiscovery, self).__init__()
        self.hosts = hosts
        self.UCAST_PORT = UCAST_PORT

        self.socket_multicast = utils.get_multicast_socket()
        utils.bind_multicast(self.socket_multicast, MCAST_GRP="224.1.1.1", MCAST_PORT=5007)

        self.socket_unicast = utils.get_unicast_socket()
        self.socket_unicast.bind(("0.0.0.0", 10001))

        self.own_address = utils.get_host_address()

    def work_func(self):
        logging.info("waiting...")

        inputready, outputready, exceptready = select([self.socket_multicast, self.socket_unicast], [], [], 1)

        for socket_data in inputready:

            data, addr = socket_data.recvfrom(1024)  # wait for a packet
            if data:
                parts = data.decode().split(":")
                if parts[0] == "SA" and addr[0] != self.own_address:
                    self.hosts.add_host(addr[0])
                    self.hosts.form_ring(self.own_address)
                    message = "RP:%s" % self.own_address
                    self.socket_unicast.sendto(message.encode(), (addr[0], self.UCAST_PORT))
                elif parts[0] == "SE":
                    logging.info("Got message for leader election!")
                    message = "RE:%s" % self.own_address
                    self.socket_unicast.sendto(message.encode(), (addr[0], self.UCAST_PORT))
                    logging.info("Send response to %s:%s" % (addr[0], self.UCAST_PORT))
