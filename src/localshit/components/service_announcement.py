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
    def __init__(self, hosts, socket_sender):
        self.hosts = hosts
        self.socket_sender = socket_sender

        self.own_address = utils.get_host_address()

    def announce_service(self):
        data = "%s:%s" % ("SA", self.own_address)
        self.socket_sender.send_message(data, type="multicast")
        logging.info("SA: service announcement...")

        self.wait_for_hosts()

    def wait_for_hosts(self):
        # Setup sockets
        self.socket_unicast = utils.get_unicast_socket()

        try:
            self.socket_unicast.bind(("0.0.0.0", 10001))
        except:
            logging.error("SA: Socket was already binded")

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
        logging.info("SA: service announcement finished.")

    def handle_service_announcement(self, addr):
        if addr[0] != self.own_address:
            self.hosts.add_host(addr[0])
            self.hosts.form_ring(self.own_address)
            message = "RP:%s" % self.own_address
            self.socket_sender.send_message(message, addr[0], type="unicast")
