"""
Client

"""
import logging
import traceback
import socket
import time
import threading
from select import select
from utils import utils


logging.basicConfig(
    level=logging.DEBUG, format="(%(threadName)-9s) %(message)s",
)


class Client:
    def __init__(self):

        self.leader_id = None
        self.own_address = utils.get_host_address()
        self.running = False
        self.connections = []
        self.counter = 0


        logging.info("client started at %s!" % self.own_address)

        # register at proxy and ask for content server
        new_message = "CL:%s" % (self.own_address)
        self.socket_proxy = utils.get_unicast_socket()
        self.socket_proxy.bind(("0.0.0.0", 10013))
        self.socket_proxy.sendto(new_message.encode(), ("172.17.0.2", 10012))
        self.connections.insert(0, self.socket_proxy)
        
        self.handle_messages(self.leader_id)


    def handle_messages(self, server_ip):
        self.running = True
        
        self.socket_content = utils.get_tcp_socket()

        # if leader ip is set, then add to connections
        if server_ip:
            logging.info("Content Server: %s" % server_ip)
            try:
                self.socket_content.connect((server_ip, 6000))
                self.connections.insert(1, self.socket_content)
            except Exception as e:
                logging.error("Error at Content Server connection: %s" % e)


        # while loop to catch messages 
        while self.running:

            inputready, outputready, exceptready = select(
                self.connections, [], [], 1
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
                        
                        # remove from list if existing
                        if self.socket_content in self.connections:
                            self.socket_content.shutdown(socket.SHUT_RDWR) 
                            self.socket_content.close()
                            self.connections.remove(self.socket_content)
                            break
                        
                    elif parts[0] == "CO":
                        logging.info("Got content: '%s' from %s" % (parts[1], socket_data.getpeername()[0]))
                    else:
                        logging.error("invalid message")
        
        time.sleep(1.1) # set pause to close socket connection correctly
        self.handle_messages(self.leader_id)
        


if __name__ == "__main__":
    try:
        logging.info("starting proxy...")
        app = Client()
    except Exception as e:
        logging.error("Error while starting app: %s" % e)
        traceback.print_exc()