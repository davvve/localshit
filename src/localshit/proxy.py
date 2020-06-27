"""
Main class for starting a proxy server.

"""
import logging
import traceback
import select
from localshit.utils import utils
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
import threading
from os import curdir, sep
import json


logging.basicConfig(
    level=logging.DEBUG, format="(%(threadName)-9s) %(message)s",
)


class ThreadingSimpleServer(ThreadingMixIn, HTTPServer):
    pass


class ProxyServer:
    def __init__(self):

        self.leader_id = "0.0.0.1"
        self.own_address = utils.get_host_address()
        self.connected_clients = []

        self.socket_unicast = utils.get_unicast_socket()
        self.socket_unicast.bind(("0.0.0.0", 10012))

        PORT = 8081

        self.Handler = self.MakeCustomHandler(self.leader_id)
        self.Handler.leader_ix = self.leader_id
        self.server = ThreadingSimpleServer(("0.0.0.0", PORT), self.Handler)

        logging.info("serving at port %s" % PORT)

        thread = threading.Thread(target=self.server.serve_forever)
        thread.daemon = True
        thread.start()

        logging.info("proxy started at %s!" % self.own_address)

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
                        self.Handler.leader_ix = parts[1]
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

    def MakeCustomHandler(self, leader):
        class MyHandler(BaseHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super(MyHandler, self).__init__(*args, **kwargs)

            def _set_headers(self):
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()

            def do_GET(self):
                try:
                    if self.path.endswith("leader"):
                        json_resp = {"leader": self.leader_ix}
                        json_str = json.dumps(json_resp)
                        self.send_response(200)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json_str.encode(encoding="utf_8"))
                    elif self.path.endswith(".html"):
                        f = open(curdir + sep + self.path, "rb")
                        self.send_response(200)
                        self.send_header("Content-type", "text/html")
                        self.end_headers()
                        self.wfile.write(f.read())
                        f.close()
                        return

                except IOError:
                    self.send_error(404, "File Not Found: %s" % self.path)

            def do_HEAD(self):
                self._set_headers()

        return MyHandler


def main():
    try:
        logging.info("starting proxy...")
        _ = ProxyServer()
    except Exception as e:
        logging.error("Error while starting app: %s" % e)
        traceback.print_exc()
