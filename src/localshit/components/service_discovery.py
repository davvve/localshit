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
        self.MCAST_GRP = MCAST_GRP
        self.MCAST_PORT = MCAST_PORT
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
        self.last_heartbeat_received = time.time()
        self.last_heartbeat_sent = (
            time.time() - 3
        )  # substract 3 sec. so that first heartbeat is sent immediately
        self.wait_for_heartbeat = False

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
                    elif parts[0] == "RR":
                        self.handle_failure_message(addr, parts)
                    else:
                        logging.error("Unknown message type: %s" % parts[0])

                    # reset heartbeat beacause of leader election or service announcement
                    self.last_heartbeat_received = time.time()

        # send heartbeat messages
        if self.election.isLeader is True:
            self.heartbeat_sender()

        # watch heartbeats
        self.watch_heartbeat()

    def watch_heartbeat(self):
        # check, when was the last heartbeat from the left neighbour?
        time_diff = time.time() - self.last_heartbeat_received
        if time_diff >= 6:

            # TODO: send failure message as multicast
            logging.info("No heartbeat received")
            right_neighbour = self.hosts.get_neighbour(direction="right")
            self.hosts.remove_host(right_neighbour)

            new_message = "RR:%s:%s" % (right_neighbour, self.own_address)
            self.socket_multicast.sendto(
                new_message.encode(), (self.MCAST_GRP, self.MCAST_PORT)
            )

            if right_neighbour == self.election.elected_leader:
                self.election.start_election()
                self.election.wait_for_response()

            self.last_heartbeat_received = time.time()

    def heartbeat_sender(self):
        # if leader, then create heartbeat message and send it every 3 sec.
        time_diff = time.time() - self.last_heartbeat_sent
        if time_diff >= 3:
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
            self.last_heartbeat_sent = time.time()

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
        # forward heartbeat message as it is, if not leader
        if self.election.isLeader is False:
            # check, if the heartbeat comes from the neighbour
            left_neighbour = self.hosts.get_neighbour(direction="left")
            right_neighbour = self.hosts.get_neighbour(direction="right")
            if addr[0] == right_neighbour:
                # forward message
                logging.info("received heartbeat. forward to %s" % left_neighbour)
                new_message = "HB:%s:%s" % (parts[1], parts[2])
                self.socket_unicast.sendto(
                    new_message.encode(), (left_neighbour, self.UCAST_PORT)
                )
                self.last_heartbeat_received = time.time()
            else:
                logging.error("received heartbeat from wrong neighbour")
        else:
            # if leader, have a look at the message if it is from himself
            if self.heartbeat_message:
                if parts[1] == self.heartbeat_message["id"]:
                    duration = time.time() - self.heartbeat_message["timestamp"]
                    logging.info(
                        "received own heartbeat from %s within %.2f sec."
                        % (addr[0], duration)
                    )
                    self.heartbeat_message = None
                    self.last_heartbeat_received = time.time()

    def handle_failure_message(self, addr, parts):
        lost_host = parts[1]

        if lost_host is not self.own_address:
            self.hosts.remove_host(lost_host)
