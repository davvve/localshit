import logging
import select
import time
from utils import utils
from utils import CompareResult

logging.basicConfig(
    level=logging.DEBUG, format="(%(threadName)-9s) %(message)s",
)


class Election:

    def __init__(self, hosts, current_member_ip):
        # first, mark member as non-participant
        self.hosts = hosts
        self.current_member_ip = current_member_ip
        self.participant = False
        self.isLeader = False
        self.got_response = False

        logging.info("Election Class initialized")

    def start_election(self):
        logging.info("starting election")
        # mark self as a participant
        self.participant = True

        # send message to left neighbour
        message = "SE:%s:%s" % (self.current_member_ip, self.isLeader)
        neighbour = self.hosts.get_neighbour()

        socket_unicast = utils.get_unicast_socket()
        socket_unicast.sendto(message.encode(), (neighbour, 10001))
        socket_unicast.close()

        self.wait_for_response()

    def wait_for_response(self):
        last_response = time.time()
        time_diff = 0

        socket_unicast = utils.get_unicast_socket()
        socket_unicast.bind(("0.0.0.0", 10001))

        while time_diff <= 1:
            try:
                inputready, outputready, exceptready = select.select([socket_unicast], [], [], 1)

                for socket_data in inputready:

                    data, addr = socket_data.recvfrom(1024)
                    if data:
                        parts = data.decode().split(":")
                        if parts[0] == "SE":
                            self.got_response = True
                            logging.info("Got response for leader election!")

            except Exception as e:
                logging.error("Error: %s" % e)

            time_diff = time.time() - last_response

        socket_unicast.close()

        if self.got_response is not True:
            logging.info("no one responds to leader elections.")

    def forward_election_message(self, message):
        compare = utils.compare_adresses(message[1], self.current_member_ip)

        socket_unicast = utils.get_unicast_socket()
        # TODO: check if message[2] is False, otherwise leader is elected

        if compare is CompareResult.LARGER:
            # TODO: forward message
            logging.info("CompareResult is larger. forward message")
            new_message = "SE:%s:%s" % (message[1], False)
            socket_unicast.sendto(new_message.encode(), (self.hosts.get_neighbour(), 10001))
        elif compare is CompareResult.LOWER and self.participant is False:
            logging.info("CompareResult is lower. update message")
            new_message = "SE:%s:%s" % (self.current_member_ip, False)
            socket_unicast.sendto(new_message.encode(), (self.hosts.get_neighbour(), 10001))
        elif compare is CompareResult.LOWER and self.participant is True:
            logging.info("Already participant of an election. Discard message")
        elif compare is CompareResult.SAME:
            logging.info("Message came back to sender. elected as leader.")
            self.isLeader = True

