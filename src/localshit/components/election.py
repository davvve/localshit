import logging
import select
import time
from utils import utils

logging.basicConfig(
    level=logging.DEBUG, format="(%(threadName)-9s) %(message)s",
)


class Election:

    def __init__(self):
        # first, mark member as non-participant
        self.participant = False
        self.isLeader = False
        self.got_response = False

        logging.info("Election Class initialized")

    def start_election(self, hosts, current_member_ip):
        logging.info("starting election")
        # mark self as a participant
        self.participant = True

        # send message to left neighbour
        message = "SE:%s:%s" % (current_member_ip, self.isLeader)
        neighbour = hosts.get_neighbour()

        socket_unicast = utils.get_unicast_socket()
        socket_unicast.sendto(message.encode(), (neighbour, 10001))
        socket_unicast.close()

        self.wait_for_response()

    def wait_for_response(self):
        last_response = time.time()
        time_diff = 0

        socket_unicast = utils.get_unicast_socket()
        socket_unicast.bind(("0.0.0.0", 10001))

        while time_diff <= 2:
            try:
                inputready, outputready, exceptready = select.select([socket_unicast], [], [], 1)

                for socket_data in inputready:

                    data, addr = socket_data.recvfrom(1024)
                    if data:
                        parts = data.decode().split(":")
                        if parts[0] == "RE":
                            self.got_response = True
                            logging.info("Got response for leader election!")

            except Exception as e:
                logging.error("Error: %s" % e)

            time_diff = time.time() - last_response

        socket_unicast.close()

        if self.got_response is not True:
            logging.info("no one responds to leader elections.")
