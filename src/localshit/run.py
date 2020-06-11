"""
Main class for starting a server instance.

"""
import sys
import time
import logging
import traceback
from components import Ring
from components import Election
from components import ServiceDiscovery
from components import ServiceAnnouncement


logging.basicConfig(
    level=logging.DEBUG, format="(%(threadName)-9s) %(message)s",
)


class LocalsHitManager:

    def __init__(self):
        self.hosts = Ring()
        self.election = Election()
        self.threads = []
        self.running = True
        logging.info("manager started!")


        # initiate service announcement thread
        announcement_thread = ServiceAnnouncement(self.hosts, self.election, 10001)
        self.threads.append(announcement_thread)


        # initiate service discovery thread
        discovery_thread = ServiceDiscovery(self.hosts, 10001)
        self.threads.append(discovery_thread)

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
            logging.error(e)
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


if __name__ == "__main__":
    try:
        logging.info("starting manager...")
        app = LocalsHitManager()
    except Exception as e:
        logging.error("Error while starting app: %s" % e)
        traceback.print_exc()
