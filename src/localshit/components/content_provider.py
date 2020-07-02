import time
import json
import random
import uuid
from localshit.utils.stop import StoppableThread
from localshit.utils.config import config
from localshit.utils.utils import logging
from localshit.components.websocket_server import WebsocketServer


class ContentProvider(StoppableThread):
    def __init__(self, election, reliable_socket, database):
        super(ContentProvider, self).__init__()
        self.election = election
        self.database = database
        self.server = WebsocketServer(config["content_websocket_port"], host="0.0.0.0")
        self.server.set_fn_new_client(self.new_client)
        self.server.set_fn_client_left(self.client_left)
        self.server.set_fn_message_received(self.message_received)
        self.quote_id = uuid.uuid4()

        # need reliable_socket for data replication
        self.reliable_socket = reliable_socket
        self.reliable_socket.set_fn_delivered(self.multicast_delivered)

        logging.debug("Starting ContentProvider")

        self.last_update = time.time()

    def work_func(self):
        if self.election.isLeader:
            if self.server.isRunning is False:
                try:
                    self.server.run_forever()
                    self.server.isRunning = True
                except Exception as e:
                    logging.error("Error while restarting server: %s" % e)
            else:
                time_diff = time.time() - self.last_update
                if time_diff >= 3:
                    logging.info("Content: publish new quote")
                    id, quote = self.get_quote("jokes.json")
                    data = "%s:%s:%s" % ("CO", id, quote)
                    # 1. Send message to client
                    try:
                        self.server.send_message_to_all(data)
                    except Exception as e:
                        logging.error("Content: Error while sending quote: %s" % e)
                        return
                    # 2. replicate with other backend servers and itself to store quote to database
                    try:
                        self.reliable_socket.multicast(data)
                    except Exception as e:
                        logging.error("Content: Error while saving quote: %s" % e)
                        return

                    self.last_update = time.time()
        else:
            if self.server.isRunning is True:
                self.server.isRunning = False
                data = "%s:%s" % ("CL", "close server")
                self.server.send_message_to_all(data)
                self.server.shutdown()
                self.server.server_close()
                logging.info("Content: publish service stopped")

    def get_quote(self, filename):
        quote = None
        quote_id = None

        try:
            file = open(filename)
            data = json.load(file)
            quotes = data["value"]
            counts = len(quotes)
            rand = random.randint(0, counts - 1)
            quote = quotes[rand]
            quote = quote["joke"]
            quote_id = uuid.uuid4()
        except Exception as e:
            logging.error("Content: Error while generating quote: %s" % e)

        return (quote_id, quote)

    # Called for every client connecting (after handshake)
    def new_client(self, client, server):
        print("Content: New client connected and was given id %d" % client["id"])
        # TODO: send last 10 updates to client

    # Called for every client disconnecting
    def client_left(self, client, server):
        print("Content: Client(%d) disconnected" % client["id"])

    # Called when a client sends a message
    def message_received(self, client, server, message):
        if len(message) > 200:
            message = message[:200] + ".."
        print("Content: Client(%d) said: %s" % (client["id"], message))

    def multicast_delivered(self, sender, message):
        logging.debug("Delivered #%s from %s" % (message, sender))
        self.database.insert(message)
