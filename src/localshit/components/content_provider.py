import logging
import time
import json
import random
from localshit.utils.stop import StoppableThread
from localshit.components.websocket_server import WebsocketServer

logging.basicConfig(
    level=logging.DEBUG, format="(%(threadName)-9s) %(message)s",
)


class ContentProvider(StoppableThread):
    def __init__(
        self, hosts, election, UCAST_PORT=10001, MCAST_GRP="224.1.1.2", MCAST_PORT=5007
    ):
        super(ContentProvider, self).__init__()
        self.election = election

        self.server = WebsocketServer(10013, host="0.0.0.0")
        self.server.set_fn_new_client(self.new_client)
        self.server.set_fn_client_left(self.client_left)
        self.server.set_fn_message_received(self.message_received)

        logging.info("Starting ContentProvider")

        self.isActive = True
        self.last_update = time.time()
        self.clients = []

    def work_func(self):
        if self.election.isLeader:
            if self.server.isRunning is False:
                self.server.run_forever()
            time_diff = time.time() - self.last_update
            if time_diff >= 3:
                logging.info("publish new quote")
                quote = self.get_quote("jokes.json")
                data = "%s:%s" % ("CO", quote)
                self.server.send_message_to_all(data)
                self.last_update = time.time()
        else:
            if self.server.isRunning is True:
                logging.info("stop server...")
                self.server.isRunning = False
                data = "%s:%s" % ("CL", "close server")
                self.server.send_message_to_all(data)
                self.server.server_close()

    def get_quote(self, filename):
        quote = None

        try:
            file = open(filename)
            data = json.load(file)
            quotes = data["value"]
            counts = len(quotes)
            rand = random.randint(0, counts - 1)
            quote = quotes[rand]
            quote = quote["joke"]
        except Exception as e:
            logging.error("Error while starting app: %s" % e)

        return quote

    # Called for every client connecting (after handshake)
    def new_client(self, client, server):
        print("New client connected and was given id %d" % client["id"])

    # Called for every client disconnecting
    def client_left(self, client, server):
        print("Client(%d) disconnected" % client["id"])

    # Called when a client sends a message
    def message_received(self, client, server, message):
        if len(message) > 200:
            message = message[:200] + ".."
        print("Client(%d) said: %s" % (client["id"], message))
