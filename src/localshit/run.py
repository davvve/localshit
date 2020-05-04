"""
Main class for starting a server instance.

"""
import socket
import os
import sys
import time
import logging

logging.basicConfig(
    level=logging.DEBUG, format="(%(threadName)-9s) %(message)s",
)

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path)
from service_discovery import ServiceDiscovery
from service_announcement import ServiceAnnouncement

if __name__ == "__main__":
    print("manager started!")
    running = True
    discovery_thread = ServiceDiscovery(10001)

    try:
        discovery_thread.start()

        logging.info("discovery_thread started")

        while running:
            if not discovery_thread.is_alive():
                print("process died")
                running = False
                break

            time.sleep(0.2)

    except KeyboardInterrupt:
        logging.info("Process terminated by user")
    except Exception as e:
        logging.error(e)
    finally:
        logging.info("stop discovery_thread...")
        discovery_thread.stop()
        discovery_thread.join()
        logging.info("discovery_thread stopped")
