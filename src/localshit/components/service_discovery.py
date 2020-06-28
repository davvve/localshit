"""
Service Announcement

Adapted from https://stackoverflow.com/questions/21089268/python-service-discovery-advertise-a-service-across-a-local-network
"""

from select import select
from localshit.utils.stop import StoppableThread
from localshit.utils import utils
import logging
import uuid
import time

logging.basicConfig(
    level=logging.DEBUG, format="(%(threadName)-9s) %(message)s",
)


class ServiceDiscovery(StoppableThread):
    def __init__(
        self, hosts, election, UCAST_PORT=10001, MCAST_GRP="224.1.1.1", MCAST_PORT=5007
    ):
        super(ServiceDiscovery, self).__init__()
        self.hosts = hosts
        self.election = election
        self.UCAST_PORT = UCAST_PORT
        self.heartbeat_message = None

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
        self.last_heartbeat = time.time()

    def work_func(self):
        logging.info("waiting...")

        # listen to incoming messages on multicast, unicast and client socket
        inputready, outputready, exceptready = select(
            [self.socket_multicast, self.socket_unicast, self.socket_content], [], [], 1
        )

        for socket_data in inputready:
            if socket_data == self.socket_content:
                client_socket, address = self.socket_content.accept()
                self.hosts.add_client(client_socket)
                logging.info("Connection from %s" % address[1])
            else:
                data, addr = socket_data.recvfrom(1024)  # wait for a packet
                if data:
                    parts = data.decode().split(":")
                    if parts[0] == "SA":
                        self.handle_service_announcement(addr)
                    elif parts[0] == "SE":
                        self.handle_election_message(addr, parts)
                    elif parts[0] == "HB":
                        # TODO: forward heartbeat
                        self.handle_heartbeat_message(addr, parts)
                    else:
                        logging.error("Unknown message type: %s" % parts[0])

        # send heartbeat messages
        if self.election.isLeader is True:
            self.heartbeat_worker(self.last_heartbeat)
        else:


    def heartbeat_worker(self, last_heartbeat):


         # checking heartbeat
        if self.heartbeat_message:
            hb_age = time.time() - self.heartbeat_message["timestamp"]
            if hb_age > 1:
                logging.error("Ring broken!")
                neighbour = self.hosts.get_neighbour()
                logging.info("Ring was broken. Lost %s" % neighbour)
                self.hosts.remove_host(neighbour)
                logging.info("Updated view: %s" % self.hosts.members)
                self.heartbeat_message = None

                if self.election.elected_leader == neighbour:
                    self.election.start_election()
                    self.election.wait_for_response()

        time_diff = time.time() - self.last_heartbeat
        if time_diff >= 3:
            logging.info("heartbeat...")
            self.last_heartbeat = time.time()

            # send new heartbeat
            self.heartbeat_message = {
                "id": str(uuid.uuid4()),
                "sender": self.own_address,
                "timestamp": time.time(),
            }

            new_message = "HB:%s:%s" % (
                self.heartbeat_message["id"],
                self.heartbeat_message["sender"],
            )
            self.socket_unicast.sendto(
                new_message.encode(), (self.hosts.get_neighbour(), 10001)
            )
            logging.info("send heartbeat to %s" % self.hosts.get_neighbour())

    def handle_service_announcement(self, addr):
        if addr[0] != self.own_address:
            self.hosts.add_host(addr[0])
            self.hosts.form_ring(self.own_address)
            message = "RP:%s" % self.own_address
            self.socket_unicast.sendto(message.encode(), (addr[0], self.UCAST_PORT))

    def handle_election_message(self, addr, parts):
        logging.info(
            "Got message for leader election from %s:%s" % (addr[0], self.UCAST_PORT)
        )
        self.election.forward_election_message(parts)

    def handle_heartbeat_message(self, addr, parts):
        # if leader, reset heartbeat message, otherwise forward it

        

        if self.heartbeat_message:
            if parts[1] == self.heartbeat_message["id"]:
                logging.info("received own heartbeat from %s" % addr[0])
                self.heartbeat_message = None
            else:
                self.forward_heartbeat(parts, addr)
                self.heartbeat_message = None
        else:
            self.forward_heartbeat(parts, addr)

    def forward_heartbeat(self, parts, addr):
        logging.info("received heartbeat. forward to %s" % self.hosts.get_neighbour())
        new_message = "HB:%s:%s" % (parts[1], parts[2])
        self.socket_unicast.sendto(new_message.encode(), (self.hosts.get_neighbour(), self.UCAST_PORT))
