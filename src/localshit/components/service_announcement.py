"""
Service Announcement

Adapted from https://stackoverflow.com/questions/21089268/python-service-discovery-advertise-a-service-across-a-local-network
"""

import time
from select import select
import logging
from localshit.utils import utils


logging.basicConfig(
    level=logging.DEBUG, format="(%(threadName)-9s) %(message)s",
)


class ServiceAnnouncement:
    def __init__(self, hosts, UCAST_PORT=10001, MCAST_GRP="224.1.1.1", MCAST_PORT=5007):
        self.hosts = hosts
        self.MCAST_GRP = MCAST_GRP
        self.MCAST_PORT = MCAST_PORT

        # Setup sockets
        self.socket_multicast = utils.get_multicast_socket()
        self.socket_unicast = utils.get_unicast_socket()
        self.socket_unicast.bind(("0.0.0.0", 10001))
        self.own_addess = utils.get_host_address()

        # start services
        self.announce_service()
        self.wait_for_hosts()

    def wait_for_hosts(self):
        last_response = time.time()
        time_diff = 0

        while time_diff <= 1:
            try:
                inputready, outputready, exceptready = select(
                    [self.socket_unicast], [], [], 1
                )

                for socket_data in inputready:

                    data, addr = socket_data.recvfrom(1024)
                    if data:
                        parts = data.decode().split(":")
                        if parts[0] == "RP":
                            self.hosts.add_host(addr[0])

            except Exception as e:
                logging.error("Error: %s" % e)

            time_diff = time.time() - last_response

        self.socket_unicast.close()
        logging.info("service announcement finished.")

    def announce_service(self):
        data = "%s:%s" % ("SA", self.own_addess)
        self.socket_multicast.sendto(data.encode(), (self.MCAST_GRP, self.MCAST_PORT))
        logging.info("service announcement...")
