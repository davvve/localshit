import logging
import select
import time
from localshit.utils import utils
from localshit.utils.utils import CompareResult

logging.basicConfig(
    level=logging.DEBUG, format="(%(threadName)-9s) %(message)s",
)


class Election:
    def __init__(self, hosts, current_member_ip, frontend="172.17.0.2"):
        # first, mark member as non-participant
        self.hosts = hosts
        self.current_member_ip = current_member_ip
        self.frontend_address = frontend
        self.participant = False
        self.isLeader = False
        self.got_response = False
        self.elected_leader = ""

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

    def wait_for_response(self):
        last_response = time.time()
        time_diff = 0

        socket_unicast = utils.get_unicast_socket()
        socket_unicast.bind(("0.0.0.0", 10001))

        while time_diff <= 1:
            try:
                inputready, outputready, exceptready = select.select(
                    [socket_unicast], [], [], 1
                )

                for socket_data in inputready:

                    data, addr = socket_data.recvfrom(1024)
                    if data:
                        parts = data.decode().split(":")
                        if parts[0] == "SE":
                            self.got_response = True
                            self.forward_election_message(parts)

            except Exception as e:
                logging.error("Error: %s" % e)

            time_diff = time.time() - last_response

        socket_unicast.close()

        if self.got_response is not True:
            logging.info("no one responds to leader elections.")
            # set self as leader
            self.elected_leader = self.current_member_ip
            self.isLeader = True
            self.send_election_to_frontend()

    def send_election_to_frontend(self):
        socket_unicast = utils.get_unicast_socket()

        new_message = "LE:%s" % self.elected_leader
        socket_unicast.sendto(new_message.encode(), (self.frontend_address, 10012))

    def forward_election_message(self, message):
        compare = utils.compare_adresses(message[1], self.current_member_ip)

        sender_id = message[1]
        leader_elected = eval(message[2])

        socket_unicast = utils.get_unicast_socket()
        # TODO: check if message[2] is False, otherwise leader is elected

        if leader_elected is False:
            if compare is CompareResult.LARGER:
                # 4.1 if id is larger, forward message to next member
                logging.info("Leader Election: id is larger. Forward message.")
                self.participant = True
                new_message = "SE:%s:%s" % (sender_id, False)
                socket_unicast.sendto(
                    new_message.encode(), (self.hosts.get_neighbour(), 10001)
                )
            elif compare is CompareResult.LOWER and self.participant is False:
                # 4.2 if id is smaller and not yes marked as participant, replace id and forward message to next member.
                self.participant = True
                logging.info(
                    "Leader Election: Sender has lower id. replace id with own id."
                )
                new_message = "SE:%s:%s" % (self.current_member_ip, False)
                socket_unicast.sendto(
                    new_message.encode(), (self.hosts.get_neighbour(), 10001)
                )
            elif compare is CompareResult.LOWER and self.participant is True:
                # 4.3 if id is smaller but already participant, then discard message
                logging.info(
                    "Leader Election: Already participant of an election. Discard message."
                )
            elif compare is CompareResult.SAME:
                # 4.4 if message came back, set itself as leader and start second part algorithm. Inform others about elected leader.
                logging.info(
                    "Leader Election: Message came back to sender. Elected as leader."
                )
                self.participant = False
                self.isLeader = True
                self.elected_leader = self.current_member_ip
                # start second part of algorithm, inform others about election
                new_message = "SE:%s:%s" % (self.current_member_ip, True)
                socket_unicast.sendto(
                    new_message.encode(), (self.hosts.get_neighbour(), 10001)
                )
                self.send_election_to_frontend()
            else:
                logging.error("Leader Election: invalid result")
        else:
            # forward message about elected leader
            if sender_id is self.current_member_ip:
                logging.info(
                    "Leader Election: Message came back to sender. Election is over. Elected Leader: %s"
                    % self.elected_leader
                )
            elif self.participant is True:
                # elected message received. mark as non-participant, record election and forward message
                self.participant = False
                self.isLeader = False
                self.elected_leader = sender_id
                logging.info(
                    "Leader Election: Election message received. note it and forward it. Elected Leader: %s"
                    % self.elected_leader
                )
                new_message = "SE:%s:%s" % (message[1], message[2])
                socket_unicast.sendto(
                    new_message.encode(), (self.hosts.get_neighbour(), 10001)
                )
            else:
                logging.info(
                    "Leader Election: Election is over. Elected Leader: %s"
                    % self.elected_leader
                )
