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
import time

logging.basicConfig(
    level=logging.DEBUG, format="(%(threadName)-9s) %(message)s",
)


class ServiceAnnouncement:

    def __init__(self, hosts, election, UCAST_PORT=10001, MCAST_GRP="224.1.1.1", MCAST_PORT=5007):
        self.hosts = hosts
        self.election = election
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

        self.announce_service()

        self.wait_for_hosts()

        

    def wait_for_hosts(self):
        last_response = time.time()
        time_diff = 0
        
        while time_diff <= 3:
            try:
                inputready, outputready, exceptready = select([self.socket_unicast], [], [], 1)

                for socket_data in inputready:

                    data, addr = socket_data.recvfrom(1024)
                    if data:
                        parts = data.decode().split(":")
                        if parts[0] == "RP":
                            self._add_to_hosts(addr[0])

            except Exception as e:
                logging.error("Error: %s" % e)

            # if no response after certain time, start election
            time_diff = time.time() - last_response

        logging.info("service announcement finished.")
        # if self.election.participant is False:
        #    self.election.start_election()

    def get_own_address(self):
        return self.own_addess

    def announce_service(self):
        data = "%s:%s" % ("SA", self.server_id)
        self.socket_multicast.sendto(data.encode(), (self.MCAST_GRP, self.MCAST_PORT))
        logging.info("service announcement...")

    def _add_to_hosts(self, host):
        self.hosts.add_host(host, self.own_addess)

