"""
Main class for starting a server instance.

"""
import socket
import os
import sys
import time
import logging
import traceback

logging.basicConfig(
    level=logging.DEBUG, format="(%(threadName)-9s) %(message)s",
)

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path)
from service_discovery import ServiceDiscovery
from service_announcement import ServiceAnnouncement


class LocalsHitManager:
    def __init__(self):
        self.threads = []
        self.running = True
        logging.info("manager started!")
        discovery_thread = ServiceDiscovery(10001)
        self.threads.append(discovery_thread)

        try:
            discovery_thread.start()

            logging.info("discovery_thread started")

            while self.running:
                for th in self.threads:
                    if not th.is_alive():
                        logging.info("Thread %s died." % th.__class__.__name)
                        self.running = False
                        break

                time.sleep(0.2)

        except KeyboardInterrupt:
            logging.info("Process terminated by user")
        except Exception as e:
            logging.error(e)
        finally:
            logging.info("stop discovery_thread...")
            for th in self.threads:
                logging.info("Stopping thread %s." % th.__class__.__name__)
                th.stop()
            for th in self.threads:
                logging.info("Joining thread %s." % th.__class__.__name__)
                th.join()
            logging.info("discovery_thread stopped")

if __name__ == "__main__":
    try:
        logging.info("starting manager...")
        app = LocalsHitManager()
    except Exception as e:
        logging.error("Error while starting app: %s" % e)
        traceback.print_exc()
