"""
Service Announcement

Adapted from https://stackoverflow.com/questions/21089268/python-service-discovery-advertise-a-service-across-a-local-network
"""

from select import select
from localshit.utils.stop import StoppableThread
from localshit.utils import utils
import logging
import time

logging.basicConfig(
    level=logging.DEBUG, format="(%(threadName)-9s) %(message)s",
)


class ServiceDiscovery(StoppableThread):
    def __init__(
        self,
        hosts,
        election,
        heartbeat,
        UCAST_PORT=10001,
        MCAST_GRP="224.1.1.1",
        MCAST_PORT=5007,
    ):
        super(ServiceDiscovery, self).__init__()
        self.hosts = hosts
        self.election = election
        self.heartbeat = heartbeat

        self.UCAST_PORT = UCAST_PORT
        self.MCAST_GRP = MCAST_GRP
        self.MCAST_PORT = MCAST_PORT

        self.socket_multicast = utils.get_multicast_socket()
        utils.bind_multicast(
            self.socket_multicast, MCAST_GRP="224.1.1.1", MCAST_PORT=5007
        )

        self.socket_unicast = utils.get_unicast_socket()
        self.socket_unicast.bind(("0.0.0.0", 10001))

        self.socket_content = utils.get_tcp_socket()
        self.socket_content.bind(("", 6000))
        self.socket_content.listen(1)

        self.own_address = utils.get_host_address()

    def work_func(self):
        # logging.info("waiting...")

        try:
            # listen to incoming messages on multicast, unicast and client socket
            inputready, outputready, exceptready = select(
                [self.socket_multicast, self.socket_unicast, self.socket_content],
                [],
                [],
                1,
            )

            for socket_data in inputready:
                if socket_data == self.socket_content:
                    client_socket, address = self.socket_content.accept()
                    self.hosts.add_client(client_socket)
                    logging.info("Content: Connection from %s" % address[1])
                else:
                    data, addr = socket_data.recvfrom(1024)  # wait for a packet
                    if data:
                        parts = data.decode().split(":")
                        if parts[0] == "SA":
                            self.handle_service_announcement(addr)
                        elif parts[0] == "SE":
                            self.election.forward_election_message(parts)
                        elif parts[0] == "HB":
                            # TODO: forward heartbeat
                            self.heartbeat.handle_heartbeat_message(addr, parts)
                        elif parts[0] == "FF":
                            self.heartbeat.handle_failure_message(addr, parts)
                        elif parts[0] == "RP":
                            logging.error("Reply from host: %s" % addr[0])
                            if addr[0] != self.own_address:
                                self.hosts.add_host(addr[0])
                        else:
                            logging.error("Unknown message type: %s" % parts[0])

                        # reset heartbeat beacause of leader election or service announcement
                        self.heartbeat.last_heartbeat_received = time.time()
        except Exception as e:
            logging.error("Error: %s" % e)

        # send heartbeat messages
        if self.election.isLeader is True:
            self.heartbeat.send_heartbeat()

        # watch heartbeats
        self.heartbeat.watch_heartbeat()

    def handle_service_announcement(self, addr):
        if addr[0] != self.own_address:
            self.hosts.add_host(addr[0])
            self.hosts.form_ring(self.own_address)
            message = "RP:%s" % self.own_address
            self.socket_unicast.sendto(message.encode(), (addr[0], self.UCAST_PORT))
        
