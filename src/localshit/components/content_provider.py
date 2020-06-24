"""
Service Announcement

Adapted from https://stackoverflow.com/questions/21089268/python-service-discovery-advertise-a-service-across-a-local-network
"""

from localshit.utils import StoppableThread
import logging
import time
import socket
import json
import random
from localshit.utils.stop import StoppableThread

logging.basicConfig(
    level=logging.DEBUG, format="(%(threadName)-9s) %(message)s",
)


class ContentProvider(StoppableThread):
    def __init__(
        self, hosts, election, UCAST_PORT=10001, MCAST_GRP="224.1.1.2", MCAST_PORT=5007
    ):
        super(ContentProvider, self).__init__()
        self.hosts = hosts
        self.election = election

        logging.info("Starting ContentProvider")

        self.isActive = True
        self.last_update = time.time()
        self.clients = []

    def work_func(self):
        
        if self.election.isLeader:
            time_diff = time.time() - self.last_update
            if time_diff >= 3:
                logging.info("publish new quote")

                quote = self.get_quote('jokes.json')
                data = "%s:%s" % ("CO", quote)
                for client in self.hosts.clients:
                    try:
                        client.send(data.encode('utf-8'))
                    except Exception:
                        logging.info("Client not available")
                        if client in self.hosts.clients:
                            self.hosts.clients.remove(client)
                self.last_update = time.time()
        else:
            for client in self.hosts.clients:
                logging.info("Shutodown socket %s" % client)
                self.hosts.clients.remove(client)


    def get_quote(self, filename):
        quote = None
        rand = random.randint(0,50)
        try:
            file = open(filename)
            data = json.load(file)
            quotes = data["value"]
            quote = quotes[rand]
            quote = quote["joke"]
        except Exception as e:
            logging.error("Error while starting app: %s" % e)

        return quote

        

