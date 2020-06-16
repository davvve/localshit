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
                self.handle_messages(self.leader_id)

    def handle_messages(self, server_ip):
        self.socket_content.connect(("172.17.0.2", 6000))

        # TODO: listen to proxy_server if new leader is there and to socket server
        # bekomme ich es mit, wenn socket server nicht mehr verfügbar ist???
        inputready, outputready, exceptready = select(
            [self.socket_unicast, self.socket_content], [], [], 1
        )

        for socket_data in inputready:

            data, addr = socket_data.recvfrom(1024)  # wait for a packet
            if data:
                parts = data.decode().split(":")
                if parts[0] == "RP":
                    # new leader there. break and handle_messages again with new_leader
                elif parts[0] == "CO":
                    logging.info(
                        "Got content from %s: %s"
                        % (addr[0], parts[1])
                    )
                else:
                    pass



if __name__ == "__main__":
    try:
        logging.info("starting proxy...")
        app = Client()
    except Exception as e:
        logging.error("Error while starting app: %s" % e)
        traceback.print_exc()
