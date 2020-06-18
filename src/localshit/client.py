"""
Client

"""
import logging
import traceback
import socket
from select import select
from utils import utils


logging.basicConfig(
    level=logging.DEBUG, format="(%(threadName)-9s) %(message)s",
)


class Client:
    def __init__(self):

        self.leader_id = "0.0.0.0"
        self.own_address = utils.get_host_address()
        self.running = False
        self.socket_servers = []

        logging.info("client started at %s!" % self.own_address)

        # initiate content server socket
        self.socket_content = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM
        )  # utils.get_unicast_socket()

        # register at proxy and ask for content server
        new_message = "CL:%s" % (self.own_address)
        self.socket_proxy = utils.get_unicast_socket()
        self.socket_proxy.bind(("0.0.0.0", 10013))
        self.socket_proxy.sendto(new_message.encode(), ("172.17.0.2", 10012))
        self.socket_servers.insert(0, self.socket_proxy)

        # set timeout. if timeout, print error
        self.handle_messages(self.leader_id)

    def handle_messages(self, server_ip):
        self.running = True
        logging.info("Content Server: %s" % server_ip)
        try:
            self.socket_content.connect((server_ip, 6000))
            self.socket_servers.insert(1, self.socket_content)
        except Exception as e:
            logging.error("No content server provided: %s" % e)

        while self.running:

            # TODO: listen to proxy_server if new leader is there and to socket server
            # bekomme ich es mit, wenn socket server nicht mehr verfügbar ist???
            inputready, outputready, exceptready = select(
                self.socket_servers, [], [], 1
            )

            for socket_data in inputready:

                data, addr = socket_data.recvfrom(1024)  # wait for a packet
                if data:
                    parts = data.decode().split(":")
                    if parts[0] == "RP":
                        # new leader there. break and handle_messages again with new_leader
                        self.running = False
                        self.leader_id = parts[1]
                        logging.info("New content server: %s" % self.leader_id)
                        # self.socket_content.close()

                    elif parts[0] == "CO":
                        logging.info("Got content")
                    else:
                        logging.error("invalid message")

        self.handle_messages(self.leader_id)


if __name__ == "__main__":
    try:
        logging.info("starting proxy...")
        app = Client()
    except Exception as e:
        logging.error("Error while starting app: %s" % e)
        traceback.print_exc()
