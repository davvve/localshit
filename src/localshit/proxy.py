"""
Main class for starting a proxy server.

"""
import logging
import traceback
import select
from localshit.utils import utils


logging.basicConfig(
    level=logging.DEBUG, format="(%(threadName)-9s) %(message)s",
)


class ProxyServer:
    def __init__(self):

        self.leader_id = "0.0.0.0"
        self.own_address = utils.get_host_address()
        self.connected_clients = []

        logging.info("proxy started at %s!" % self.own_address)

        self.socket_unicast = utils.get_unicast_socket()
        self.socket_unicast.bind(("0.0.0.0", 10012))

        while True:
            inputready, outputready, exceptready = select.select(
                [self.socket_unicast], [], [], 1
            )

            for socket_data in inputready:

                data, addr = socket_data.recvfrom(1024)  # wait for a packet
                if data:
                    parts = data.decode().split(":")
                    if parts[0] == "CL":
                        logging.info("Client connected with IP %s" % addr[0])
                        if addr not in self.connected_clients:
                            self.connected_clients.append(addr)
                        self.handle_client_request(addr, self.leader_id)
                    elif parts[0] == "LE":
                        logging.info("Leader elected: %s" % parts[1])
                        self.leader_id = parts[1]
                        self.inform_clients_about_leader(
                            self.leader_id, self.connected_clients
                        )

    def handle_client_request(self, addr, leader_id):
        new_message = "RP:%s" % (leader_id)
        socket_sender = utils.get_unicast_socket()
        socket_sender.sendto(new_message.encode(), (addr[0], 10013))
        logging.info("message sent to: %s:10012" % addr[0])

    def inform_clients_about_leader(self, leader_id, clients):
        for client in clients:
            self.handle_client_request(client, leader_id)


if __name__ == "__main__":
    try:
        logging.info("starting proxy...")
        app = ProxyServer()
    except Exception as e:
        logging.error("Error while starting app: %s" % e)
        traceback.print_exc()
