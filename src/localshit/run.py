"""
Main class for starting a server instance.

"""
import time
import logging
import traceback
from localshit.components.ring import Ring
from localshit.components.election import Election
from localshit.components.service_discovery import ServiceDiscovery
from localshit.components.service_announcement import ServiceAnnouncement
from localshit.components.content_provider import ContentProvider
from localshit.components.webserver import StatusServer  # noqa: F401
from localshit.utils import utils


logging.basicConfig(
    level=logging.DEBUG, format="(%(threadName)-9s) %(message)s",
)


class LocalsHitManager:
    def __init__(self, proxy="172.17.0.2"):
        self.threads = []
        self.running = True
        logging.info("manager started!")

        self.own_address = utils.get_host_address()
        self.hosts = Ring(self.own_address)

        # start service announcement
        _ = ServiceAnnouncement(self.hosts, 10001)

        self.hosts.add_host(self.own_address)
        self.hosts.form_ring(self.own_address)

        # start election
        self.election = Election(self.hosts, self.own_address, proxy=proxy)
        self.election.start_election()
        self.election.wait_for_response()

        # initiate service discovery thread
        discovery_thread = ServiceDiscovery(self.hosts, self.election)
        self.threads.append(discovery_thread)

        # initiate Content Provider
        content_provider = ContentProvider(self.hosts, self.election)
        self.threads.append(content_provider)
        # optional, webserver for status
        # _ = StatusServer(self.hosts, self.election)

        try:
            # start threads
            for th in self.threads:
                th.start()

            # monitor threads and exit on failing
            while self.running:
                for th in self.threads:
                    if not th.is_alive():
                        logging.info("Thread %s died." % th.__class__.__name__)
                        self.running = False
                        break

                time.sleep(0.2)

        except KeyboardInterrupt:
            logging.info("Process terminated by user")
        except Exception as e:
            logging.error("Error in run.py: %s" % e)
            traceback.print_exc()
        finally:
            # graceful shutdown
            logging.info("stopping threads...")
            for th in self.threads:
                logging.info("Stopping thread %s." % th.__class__.__name__)
                th.stop()
            for th in self.threads:
                logging.info("Joining thread %s." % th.__class__.__name__)
                th.join()
            logging.info("threads stopped")
