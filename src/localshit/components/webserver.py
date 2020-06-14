import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn

logging.basicConfig(
    level=logging.DEBUG, format="(%(threadName)-9s) %(message)s",
)


def MakeCustomHandler(hosts, election):
    class MyHandler(BaseHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            self.hosts = hosts
            self.election = election
            super(MyHandler, self).__init__(*args, **kwargs)

        def _set_headers(self):
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

        def _html(self, message):
            """This just generates an HTML document that includes `message`
            in the body. Override, or re-write this do do more interesting stuff.
            """
            hosts_list = self.hosts.get_hosts()
            content = (
                f"<html><body><h1>{message}</h1><br><p>{hosts_list}</p></body></html>"
            )
            return content.encode("utf8")  # NOTE: must return a bytes object!

        def do_GET(self):
            self._set_headers()
            self.wfile.write(self._html("Distributed systems"))

        def do_HEAD(self):
            self._set_headers()

    return MyHandler


class ThreadingSimpleServer(ThreadingMixIn, HTTPServer):
    pass


class StatusServer:
    def __init__(self, hosts, election):
        self.hosts = hosts
        self.election = election

        PORT = 8000

        Handler = MakeCustomHandler(self.hosts, self.election)
        server = ThreadingSimpleServer(("0.0.0.0", PORT), Handler)

        logging.info("serving at port %s" % PORT)

        thread = threading.Thread(target=server.serve_forever)
        thread.daemon = True
        thread.start()
