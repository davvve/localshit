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
        # logging.info("waiting...")

        try:
            # listen to incoming messages on multicast, unicast and client socket
            inputready, outputready, exceptready = select(
                [self.socket_multicast, self.socket_unicast, self.socket_content], [], [], 1
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
                            self.handle_election_message(addr, parts)
                        elif parts[0] == "HB":
                            # TODO: forward heartbeat
                            self.handle_heartbeat_message(addr, parts)
                        elif parts[0] == "FF":
                            self.handle_failure_message(addr, parts)
                        elif parts[0] == "RP":
                            logging.error("Reply host: %s" % parts[0])
                            if addr[0] != self.own_address:
                                self.hosts.add_host(addr[0])
                        else:
                            logging.error("Unknown message type: %s" % parts[0])

                        # reset heartbeat beacause of leader election or service announcement
                        self.last_heartbeat_received = time.time()
        except Exception as e:
            logging.error("Error: %s" % e)

        # send heartbeat messages
        if self.election.isLeader is True:
            self.last_heartbeat_sent = self.heartbeat_sender(self.last_heartbeat_sent)

        # watch heartbeats
        self.last_heartbeat_received = self.watch_heartbeat(
            self.last_heartbeat_received
        )

    def watch_heartbeat(self, last_heartbeat_received):
        # check, when was the last heartbeat from the left neighbour?
        time_diff = time.time() - last_heartbeat_received
        if time_diff >= 6:
            failed_neighbour = self.hosts.get_neighbour(direction="right")

            # if own address, then do nothing
            if failed_neighbour is not self.own_address:
                # remove failed neighbour
                logging.info("Heartbeat: nothing received from %s" % failed_neighbour)
                self.hosts.remove_host(failed_neighbour)

                # send failure message as multicast
                new_message = "FF:%s:%s" % (failed_neighbour, self.own_address)
                self.socket_multicast.sendto(
                    new_message.encode(), (self.MCAST_GRP, self.MCAST_PORT)
                )

                # if this was leader, then start service announcement and leader election
                if failed_neighbour == self.election.elected_leader:
                    data = "%s:%s" % ("SA", self.own_address)
                    self.socket_multicast.sendto(
                        data.encode(), (self.MCAST_GRP, self.MCAST_PORT)
                    )
                    self.election.start_election()
                    self.election.wait_for_response()

                return time.time()
            else:
                return time.time()
        else:
            return last_heartbeat_received

    def heartbeat_sender(self, last_heartbeat_sent):
        # create heartbeat message and send it every 3 sec.
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

            logging.info("Heartbeat: send to %s" % self.hosts.get_neighbour())
            return time.time()
        else:
            return last_heartbeat_sent

    def handle_service_announcement(self, addr):
        if addr[0] != self.own_address:
            self.hosts.add_host(addr[0])
            self.hosts.form_ring(self.own_address)
            message = "RP:%s" % self.own_address
            self.socket_unicast.sendto(message.encode(), (addr[0], self.UCAST_PORT))

    def handle_election_message(self, addr, parts):
        self.election.forward_election_message(parts)

    def handle_heartbeat_message(self, addr, parts):
        # forward heartbeat message as it is, if not leader
        if self.election.isLeader is False:
            # check, if the heartbeat comes from the neighbour
            left_neighbour = self.hosts.get_neighbour(direction="left")
            right_neighbour = self.hosts.get_neighbour(direction="right")
            # cehck, if heartbeat comes from the right neighbour
            if addr[0] == right_neighbour:
                # forward message
                logging.info("Heartbeat: received. forward to %s" % left_neighbour)
                new_message = "HB:%s:%s" % (parts[1], parts[2])
                self.socket_unicast.sendto(
                    new_message.encode(), (left_neighbour, self.UCAST_PORT)
                )
                # note time of last heartbeat
                self.last_heartbeat_received = time.time()
            else:
                logging.error("Heartbeat: received from wrong neighbour")
        else:
            # if leader, have a look at the message if it is from himself
            if self.heartbeat_message:
                if parts[1] == self.heartbeat_message["id"]:
                    duration = time.time() - self.heartbeat_message["timestamp"]
                    logging.info(
                        "Heartbeat: received own heartbeat from %s."
                        % addr[0]
                    )
                    self.heartbeat_message = None
                    self.last_heartbeat_received = time.time()

    def handle_failure_message(self, addr, parts):
        lost_host = parts[1]
        # remove failed host from list
        if lost_host != self.own_address:
            self.hosts.remove_host(lost_host)
