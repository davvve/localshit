"""
Client

"""
import logging
import traceback
from utils import utils


logging.basicConfig(
    level=logging.DEBUG, format="(%(threadName)-9s) %(message)s",
)


class Client:
    def __init__(self):

        self.leader_id = ""
        self.own_address = utils.get_host_address()

        logging.info("proxy started at %s!" % self.own_address)

        new_message = "CL:%s" % (self.own_address)
        socket_unicast = utils.get_unicast_socket()
        socket_unicast.sendto(new_message.encode(), ("172.17.0.2", 10012))

        socket_unicast.settimeout(1.0)
        data, server = socket_unicast.recvfrom(1024)
        if data:
            parts = data.decode().split(":")
            if parts[0] == "RP":
                logging.info("Message received: %s" % parts[1])
                self.leader_id = parts[1]


if __name__ == "__main__":
    try:
        logging.info("starting proxy...")
        app = Client()
    except Exception as e:
        logging.error("Error while starting app: %s" % e)
        traceback.print_exc()
